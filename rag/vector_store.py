import faiss
import pickle
from pathlib import Path

class VectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.chunk_metadata = []

    def add(self, embeddings, chunks):
        self.index.add(embeddings)
        self.chunk_metadata.extend(chunks)

    def search(self, query_embedding, k: int = 5):
        distances, indices = self.index.search(query_embedding, k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            chunk = self.chunk_metadata[idx]
            results.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"],
                "distance": float(dist)
            })
        return results

    def save(self, folder_path: str):
        folder = Path(folder_path)
        folder.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(folder / "index.faiss"))
        with open(folder / "metadata.pkl", "wb") as f:
            pickle.dump(self.chunk_metadata, f)

    @classmethod
    def load(cls, folder_path: str, dimension: int):
        folder = Path(folder_path)
        store = cls(dimension)
        store.index = faiss.read_index(str(folder / "index.faiss"))
        with open(folder / "metadata.pkl", "rb") as f:
            store.chunk_metadata = pickle.load(f)
        return store