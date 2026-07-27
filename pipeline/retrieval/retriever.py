import time
from langchain_community.vectorstores import Chroma
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

    def retrieve_context(self, query: str, k: int = 4) -> list:
        """Retrieves top-k relevant documents from ChromaDB with a score threshold filter."""
        results = self.vector_db.similarity_search_with_score(query, k=k)
        return results

    def answer_query(self, query: str) -> dict:
        """Retrieves context and extracts exact verbatim answers citing page numbers."""
        
        # 1. Retrieve the relevant chunks from ChromaDB
        docs = self.vector_db.similarity_search(query, k=10)
        
        if not docs:
            return {
                "answer": "The requested information is not available in the indexed educational material.",
                "sources": []
            }
            
        # 2. Format the context (Injecting page numbers for the LLM) and extract sources
        context = ""
        sources = []
        for doc in docs:
            meta = doc.metadata
            book_type = meta.get("book_type", "Unknown")
            chapter = meta.get("chapter", "Unknown")
            page = meta.get("page_number", "Unknown")
            
            # CRITICAL: Show the page number to the LLM so it can cite it
            context += f"--- Page {page} ---\n{doc.page_content}\n\n"
            
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