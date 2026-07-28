import os
import re
import json
from typing import Optional, Dict, List, Any
from PIL import Image

from langchain_community.vectorstores import Chroma
from embeddings.embedding_model import embedding_loader  # Using your existing embedding loader

class ImageRetriever:
    def __init__(
        self,
        manifest_path: str = "figure1_output - Copy/Biology-Manifest-Class11.json",
        persist_directory: str = "vector_db/chroma_images",
        collection_name: str = "biology_figures"
    ):
        self.manifest_path = manifest_path
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_function = embedding_loader.get_embedding_model()
        
        # Load JSON Manifest in memory for instant exact figure number lookups
        self.manifest_data = self._load_manifest()
        
        # Initialize or load the Chroma collection specifically for figures
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory
        )
        
        # Auto-index images if Chroma database isn't built yet
        if self.vector_store._collection.count() == 0:
            print("[*] Indexing figure captions and metadata into vector store...")
            self._build_image_index()

    def _load_manifest(self) -> List[Dict[str, Any]]:
        """Loads figure metadata from the JSON manifest file."""
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"[!] Warning: Manifest file not found at {self.manifest_path}")
            return []

    def _build_image_index(self):
        """Indexes figure captions into ChromaDB for semantic search."""
        documents = []
        metadatas = []
        ids = []

        for idx, item in enumerate(self.manifest_data):
            # Extract standard JSON keys
            fig_num = str(item.get("figure_number", "")).strip().lower()
            caption = item.get("caption", "") or item.get("description", "")
            
            # CHANGED: Now successfully grabs the "image" key from your JSON
            img_path = item.get("image", "") or item.get("image_path", "") or item.get("file_path", "")

            if caption:
                documents.append(caption)
                metadatas.append({
                    "figure_number": fig_num,
                    "image_path": img_path,
                    "caption": caption
                })
                ids.append(f"fig_{idx}")

        if documents:
            self.vector_store.add_texts(
                texts=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[+] Successfully indexed {len(documents)} figures.")

    def _extract_figure_number(self, query: str) -> Optional[str]:
        """Detects if query contains a figure number like '1.1', '1.10', or 'fig 1.3'."""
        pattern = r'(?:fig(?:ure)?\.?\s*)?(\d+\.\d+)'
        match = re.search(pattern, query.lower())
        if match:
            return match.group(1)  # Returns e.g. "1.1"
        return None

    def get_by_figure_number(self, fig_num: str) -> Optional[Dict[str, Any]]:
        """Looks up an image directly by its figure number."""
        fig_num_clean = fig_num.strip().lower()
        
        for item in self.manifest_data:
            num = str(item.get("figure_number", "")).strip().lower()
            if num == fig_num_clean or num.endswith(fig_num_clean):
                # CHANGED: Ensures direct lookups also use the correct key
                img_path = item.get("image", "") or item.get("image_path", "") or item.get("file_path", "")
                return {
                    "figure_number": item.get("figure_number"),
                    "caption": item.get("caption", "") or item.get("description", ""),
                    "image_path": img_path,
                    "match_type": "Direct Figure Number Match"
                }
        return None

    def get_by_description(self, query: str, top_k: int = 1) -> List[Dict[str, Any]]:
        """Searches for images based on semantic similarity of the query to figure captions."""
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        images = []
        for doc, score in results:
            images.append({
                "figure_number": doc.metadata.get("figure_number"),
                "caption": doc.page_content,
                "image_path": doc.metadata.get("image_path"),
                "score": float(score),
                "match_type": "Semantic Description Match"
            })
        return images

    def retrieve_image(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for image retrieval.
        Routes to exact figure number lookup if pattern exists, else performs semantic search.
        """
        # 1. Check if user typed a figure number
        fig_num = self._extract_figure_number(query)
        if fig_num:
            direct_match = self.get_by_figure_number(fig_num)
            if direct_match:
                return {"status": "success", "data": [direct_match]}

        # 2. THE GUARD: Only do semantic search if they actually ask for a visual
        image_keywords = ['figure', 'fig', 'image', 'diagram', 'picture', 'show']
        if not any(kw in query.lower() for kw in image_keywords):
            return {"status": "not_found", "message": "Not an image query, fallback to text RAG."}

        # 3. Fallback to semantic caption search
        desc_matches = self.get_by_description(query, top_k=1)
        if desc_matches:
            return {"status": "success", "data": desc_matches}

        return {"status": "not_found", "message": "No relevant figure found for the query."}


# Global instance
image_retriever = ImageRetriever()