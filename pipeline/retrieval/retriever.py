import time
import re
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document  
from config.settings import CHROMA_PERSIST_DIR
from embeddings.embedding_model import embedding_loader
from models.llm_factory import LLMFactory
from pipeline.prompts.prompts import build_qa_prompt
from models.model_selector import model_selector

class RAGPipeline:
    def __init__(self):
        print("[*] Initializing Strict RAG Retrieval Pipeline...")
        self.embedding_model = embedding_loader.get_embedding_model()
        self.vector_db = Chroma(
            persist_directory=str(CHROMA_PERSIST_DIR),
            embedding_function=self.embedding_model
        )

    def retrieve_context(self, query: str, k: int = 5) -> list:
        """Retrieves top-k relevant documents from ChromaDB with a score threshold filter."""
        results = self.vector_db.similarity_search_with_score(query, k=k)
        return results

    def _build_strict_filter(self, query: str) -> dict | None:
        """
        Analyzes the query to enforce strict routing to the Textbook or Guide.
        Returns a ChromaDB filter dictionary or None if no strict rules apply.
        """
        query_lower = query.lower()

        # The foolproof way to match all guide types without relying on $contains
        guide_filter = {
            "$or": [
                {"book_type": "Guide"},
                {"book_type": "Guide - MCQs"},
                {"book_type": "Guide - Short Qs"},
                {"book_type": "Guide - Long Qs"}
            ]
        }

        # RULE 1: Explicit Override Commands
        if "from book" in query_lower:
            return {"book_type": "Textbook"}
            
        if "from guide" in query_lower:
            return guide_filter

        # RULE 2: Implicit Guide Keywords 
        guide_keywords = ["exercise", "mcq", "mcqs", "short question", "long question"]
        if any(kw in query_lower for kw in guide_keywords):
            return guide_filter

        # No strict rules applied, search everywhere natively
        return None

    def answer_query(self, query: str, force_book_type: str | None = None) -> dict:
        """Retrieves context using strict metadata routing and extracts exact answers."""
        
        docs = []
        
        # --- INTENT PARSING ---
        page_match = re.search(r'\b(?:page|pg\.?)\s*(\d+)\b', query, re.IGNORECASE)
        
        # Ensure we don't confuse image requests for topic numbers
        if re.search(r'\b(?:fig(?:ure)?|image|img|pic(?:ture)?|photo(?:graph)?|diagram|illustration)\b\s*[-_]?\s*\d+\.\d+', query, re.IGNORECASE):
            topic_match = None  
        else:
            topic_match = re.search(r'(?:topic\s*)?(\d+\.\d+)\b', query, re.IGNORECASE)

        # Generate strict source filter (Book vs Guide)
        strict_filter = self._build_strict_filter(query)
        # If a caller explicitly forces a book type, override strict_filter
        if force_book_type:
            if force_book_type.lower().startswith("guide"):
                strict_filter = {
                    "$or": [
                        {"book_type": "Guide"},
                        {"book_type": "Guide - MCQs"},
                        {"book_type": "Guide - Short Qs"},
                        {"book_type": "Guide - Long Qs"}
                    ]
                }
            else:
                strict_filter = {"book_type": "Textbook"}

        # --- EXECUTE STRICT SEARCHES ---
        
        # 1. EXPLICIT PAGE REQUEST
        if page_match:
            target_page = int(page_match.group(1))
            print(f"[*] Detected explicit page request for Page {target_page}. Applying strict metadata filter...")
            
            # Combine page filter with book/guide filter if one exists
            if strict_filter:
                combined_filter = {"$and": [{"page_number": target_page}, strict_filter]}
            else:
                combined_filter = {"page_number": target_page}
                
            docs = self.vector_db.similarity_search(query, k=10, filter=combined_filter) # type: ignore
            
        # 2. EXPLICIT TOPIC REQUEST
        elif topic_match:
            target_topic = topic_match.group(1)
            print(f"[*] Detected explicit topic request for Topic {target_topic}. Fetching exact textbook sections...")
            
            try:
                collection = self.vector_db._collection
                
                results = collection.get(
                    where={"book_type": "Textbook"},
                    where_document={"$contains": target_topic},
                    include=["documents", "metadatas"]
                )
                
                docs_list = results.get("documents") or []
                meta_list = results.get("metadatas") or []
                
                for doc_text, meta in zip(docs_list, meta_list):
                    if doc_text and meta:
                        # THE FIX: If the text chunk is just a figure caption, IGNORE IT!
                        # This forces the database to find the actual long textbook paragraphs for the topic.
                        is_figure = f"Figure {target_topic}" in doc_text or f"FIGURE {target_topic}" in doc_text
                        if is_figure and len(doc_text.strip()) < 250:
                            continue # Skip this tiny caption and keep looking for the real topic!
                            
                        docs.append(Document(page_content=doc_text, metadata=meta))
                        
                docs = docs[:10]
                
            except Exception as e:
                print(f"[-] Database text-scan error: {e}")

            if not docs:
                print(f"[-] Exact Topic {target_topic} not found natively. Falling back to semantic search...")
                docs = self.vector_db.similarity_search(query, k=10, filter={"book_type": "Textbook"}) # type: ignore
        else:
            # General / conceptual queries (multi-word topics without numeric markers)
            print("[*] Performing general semantic retrieval for conceptual/multi-word query...")
            # Use similarity search with scoring to better handle multi-word conceptual strings
            scored_results = self.vector_db.similarity_search_with_score(query, k=10)
            docs = []
            for doc, score in scored_results:
                # Normalize doc content to string to avoid type issues
                meta = {}
                content_str = ""
                try:
                    if hasattr(doc, 'page_content'):
                        content_str = str(getattr(doc, 'page_content', ''))
                        meta = getattr(doc, 'metadata', {}) or {}
                    else:
                        content_str = str(doc)
                except Exception:
                    content_str = str(doc)

                # Skip tiny caption-like chunks when user asks for in-depth explanation
                query_lower = query.lower()
                explanation_keywords = ["explain", "describe", "what is", "define", "definition", "ionization", "process", "mechanism"]
                if any(kw in query_lower for kw in explanation_keywords) and len(content_str.strip()) < 200:
                    continue

                docs.append(Document(page_content=content_str, metadata=meta))

            # If we filtered out too aggressively, expand search and retry
            if not docs:
                print("[*] No suitable long documents found; expanding search to k=20 and relaxing length filter...")
                scored_results = self.vector_db.similarity_search_with_score(query, k=20)
                for doc, score in scored_results:
                    meta = {}
                    content_str = ""
                    try:
                        if hasattr(doc, 'page_content'):
                            content_str = str(getattr(doc, 'page_content', ''))
                            meta = getattr(doc, 'metadata', {}) or {}
                        else:
                            content_str = str(doc)
                    except Exception:
                        content_str = str(doc)

                    if len(content_str.strip()) < 120:
                        continue
                    docs.append(Document(page_content=content_str, metadata=meta))
            docs = docs[:10]
            
        # Format the context and extract sources cleanly
        context = ""
        sources = []
        for doc in docs:
            meta = doc.metadata
            book_type = meta.get("book_type", "Unknown")
            chapter = meta.get("chapter", "Unknown")
            page = meta.get("page_number", -1)
            
            # Context injection for the LLM
            if page != -1:
                context += f"--- Page {page} ---\n{doc.page_content}\n\n"
            else:
                context += f"--- Source: {book_type} ({chapter}) ---\n{doc.page_content}\n\n"
            
            # Professional source formatting
            if page == -1 or str(page) == "-1":
                sources.append(f"[{book_type} | {chapter}]")
            else:
                sources.append(f"[{book_type} | {chapter} | Page: {page}]")
            
        # Remove duplicate sources cleanly
        sources = list(dict.fromkeys(sources))
        
        # Decide whether to return verbatim source text or call LLM
        # By default prefer verbatim extraction from books unless user asks for summarization/paraphrase
        q_lower = query.lower()
        paraphrase_keywords = ["summarize", "in your own words", "paraphrase", "brief", "short", "simplify", "explain in simple"]
        needs_paraphrase = any(k in q_lower for k in paraphrase_keywords)

        # If the user asked for an explicit topic or an explanation, return the concatenated source paragraphs verbatim
        if topic_match or any(kw in q_lower for kw in ["explain", "describe", "define", "salient features", "what is", "characteristics"]) and not needs_paraphrase:
            # Concatenate page contents preserving original wording; limit overall length to avoid huge payloads
            concatenated = "\n\n".join([d.page_content for d in docs if getattr(d, 'page_content', None)])
            if not concatenated.strip() and docs:
                concatenated = docs[0].page_content

            # Trim if excessively long (keep up to ~30k chars)
            max_chars = 30000
            if len(concatenated) > max_chars:
                concatenated = concatenated[:max_chars] + "\n\n[Truncated source content...]"

            return {
                "answer": concatenated.strip(),
                "sources": sources
            }

        # Otherwise, use the centralized prompt builder from prompts.py and call LLM for a generated answer
        system_instruction, final_prompt = build_qa_prompt(query, context)
        answer = LLMFactory.generate_response(
            prompt=final_prompt, 
            system_instruction=system_instruction
        )
        
        return {
            "answer": answer.strip(),
            "sources": sources
        }

# Singleton instance
rag_pipeline = RAGPipeline()