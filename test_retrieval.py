from rag.vector_store import VectorStore
from rag.retriever import Retriever

EMBEDDING_DIM = 384
INDEX_FOLDER = "Data/index"

store = VectorStore.load(INDEX_FOLDER, EMBEDDING_DIM)
retriever = Retriever(store)

results = retriever.retrieve("AI systems should have human oversight", k=3)

for r in results:
    print("SOURCE:", r["source"])
    print("TEXT:", r["text"][:300])
    print("DISTANCE:", r["distance"])
    print("---")