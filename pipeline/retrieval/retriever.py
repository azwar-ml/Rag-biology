import time
import re
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document  # <-- Added this import
from config.settings import CHROMA_PERSIST_DIR
from embeddings.embedding_model import embedding_loader
from models.llm_factory import LLMFactory
from pipeline.prompts.prompts import build_qa_prompt
from models.model_selector import model_selector

class RAGPipeline:
    def __init__(self):
        print("[*] Initializing RAG Retrieval Pipeline...")
        self.embedding_model = embedding_loader.get_embedding_model()
        self.vector_db = Chroma(
            persist_directory=str(CHROMA_PERSIST_DIR),
            embedding_function=self.embedding_model
        )

    def retrieve_context(self, query: str, k: int = 5) -> list:
        """Retrieves top-k relevant documents from ChromaDB with a score threshold filter."""
        results = self.vector_db.similarity_search_with_score(query, k=k)
        return results

    def answer_query(self, query: str) -> dict:
        """Retrieves context and extracts exact verbatim answers citing page numbers."""
        
        docs = []
        
        # --- INTENT 1: EXPLICIT PAGE REQUEST (e.g., "What is on page 47") ---
        page_match = re.search(r'\b(?:page|pg\.?)\s*(\d+)\b', query, re.IGNORECASE)
        
        if re.search(r'\b(?:fig(?:ure)?|image|img|pic(?:ture)?|photo(?:graph)?|diagram|illustration)\b\s*[-_]?\s*\d+\.\d+', query, re.IGNORECASE):
            topic_match = None  
        else:
            topic_match = re.search(r'(?:topic\s*)?(\d+\.\d+)\b', query, re.IGNORECASE)

        # --- INTENT 1: EXPLICIT PAGE REQUEST ---
        if page_match:
            target_page = int(page_match.group(1))
            print(f"[*] Detected explicit page request for Page {target_page}. Applying strict metadata filter...")
            docs = self.vector_db.similarity_search(query, k=10, filter={"page_number": target_page}) # type: ignore
            
        elif topic_match:
            target_topic = topic_match.group(1)
            print(f"[*] Detected explicit topic request for Topic {target_topic}. Filtering natively...")
            
            docs = []
            try:
                collection = self.vector_db._collection
                
                # 1. Native Database Filter: Look in Metadata first (limit=50 to prevent truncation)
                results = collection.get(
                    where={"topic": {"$contains": target_topic}},
                    limit=50,
                    include=["documents", "metadatas"]
                )
                
                docs_list = results.get("documents") or []
                meta_list = results.get("metadatas") or []
                
                # 2. Native Database Filter: If metadata fails, search RAW TEXT natively!
                if not docs_list:
                    print(f"[-] Topic {target_topic} not found in metadata. Querying entire database text natively...")
                    results = collection.get(
                        where_document={"$contains": target_topic},
                        limit=50,
                        include=["documents", "metadatas"]
                    )
                    docs_list = results.get("documents") or []
                    meta_list = results.get("metadatas") or []
                
                # Convert the raw database results back into LangChain Document objects
                for doc_text, meta in zip(docs_list, meta_list):
                    if meta is not None:
                        docs.append(Document(page_content=doc_text or "", metadata=meta))
                        
                docs = docs[:10] # Keep the top 10 most relevant chunks
            except Exception as e:
                print(f"[-] Native lookup error: {e}")

            # 3. Ultimate Fallback to Semantic Search
            if not docs:
                print(f"[-] No direct match for {target_topic} found anywhere. Falling back to semantic search.")
                docs = self.vector_db.similarity_search(query, k=10)
        
        else:
            # --- ADDED: Standard semantic search fallback for regular questions ---
            print(f"[*] Performing standard semantic search...")
            docs = self.vector_db.similarity_search(query, k=10)
        
        if not docs:
            return {
                "answer": "The requested information is not available in the indexed educational material.",
                "sources": []
            }
            
        # 2. Format the context and extract sources cleanly
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
            
            # PROFESSIONAL SOURCE FORMATTING: Omit "-1" for guides
            if page == -1 or str(page) == "-1":
                sources.append(f"[{book_type} | {chapter}]")
            else:
                sources.append(f"[{book_type} | {chapter} | Page: {page}]")
            
        # Remove duplicate sources cleanly
        sources = list(dict.fromkeys(sources))
        
        # 3. Use the centralized prompt builder from prompts.py
        system_instruction, final_prompt = build_qa_prompt(query, context)
        
        # 4. Generate the response
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