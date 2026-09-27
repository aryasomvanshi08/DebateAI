from rag.document_loader import load_documents_from_folder
from rag.chunker import chunk_documents
from rag.embeddings import embed_texts
from rag.vector_store import VectorStore

DOCS_FOLDER = "Data/Documents"
INDEX_FOLDER = "Data/index"
EMBEDDING_DIM = 384

def build():
    print("Loading documents...")
    documents = load_documents_from_folder(DOCS_FOLDER)
    print(f"Loaded {len(documents)} documents.")

    print("Chunking...")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    print("Embedding chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    print("Building FAISS index...")
    store = VectorStore(dimension=EMBEDDING_DIM)
    store.add(embeddings, chunks)

    print("Saving index...")
    store.save(INDEX_FOLDER)
    print("Done. Index saved to", INDEX_FOLDER)

if __name__ == "__main__":
    build()