from embeddings.embedding_model import embedding_loader

class EmbeddingGenerator:
    def __init__(self):
        self.model = embedding_loader.get_embedding_model()

    def embed_documents(self, texts: list[str]):
        """Generates vector embeddings for a list of document strings."""
        return self.model.embed_documents(texts)

    def embed_query(self, query: str):
        """Generates vector embedding for a single user query."""
        return self.model.embed_query(query)