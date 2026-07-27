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
        """Retrieves context, selects the correct model/prompt, and generates an answer."""
        
        # 1. Retrieve the relevant chunks from ChromaDB
        docs = self.vector_db.similarity_search(query, k=4)
        
        if not docs:
            return {
                "answer": "The requested information is not available in the indexed educational material.",
                "sources": []
            }
            
        # 2. Format the context and extract sources
        context = ""
        sources = []
        for doc in docs:
            context += f"{doc.page_content}\n\n"
            meta = doc.metadata
            book_type = meta.get("book_type", "Unknown")
            chapter = meta.get("chapter", "Unknown")
            page = meta.get("page_number", "Unknown")
            sources.append(f"[{book_type} | {chapter} | Page: {page}]")
            
        # Remove duplicate sources cleanly
        sources = list(dict.fromkeys(sources))
        
        # 3. Analyze the task to get the dynamic prompt and model
        task_info = model_selector.analyze_task(query)
        system_instruction = task_info["system_prompt"]
        
        # 4. Build the final prompt for the LLM
        final_prompt = f"Context:\n{context}\n\nUser Question:\n{query}"
        
        # 5. Generate the response
        answer = LLMFactory.generate_response(
            prompt=final_prompt, 
            system_instruction=system_instruction
        )
        
        return {
            "answer": answer,
            "sources": sources
        }

# Singleton instance
rag_pipeline = RAGPipeline()