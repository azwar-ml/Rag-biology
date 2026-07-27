import os
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingModelLoader:
    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5"):
        self.model_name = model_name
        self._model = None

    def get_embedding_model(self):
        """Loads and returns the sentence transformer embedding model."""
        if self._model is None:
            print(f"[*] Loading embedding model: {self.model_name}...")
            self._model = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("[+] Embedding model loaded successfully.")
        return self._model

# Singleton instance
embedding_loader = EmbeddingModelLoader()