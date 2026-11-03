from rag.embeddings import embed_texts

class Retriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def retrieve(self, query: str, k: int = 5) -> list[dict]:
        query_embedding = embed_texts([query])
        return self.vector_store.search(query_embedding, k=k)