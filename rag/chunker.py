def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    text = text.strip()
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks

def chunk_documents(documents: dict, chunk_size: int = 800, overlap: int = 100) -> list[dict]:
    all_chunks = []
    for filename, text in documents.items():
        text_chunks = chunk_text(text, chunk_size, overlap)
        for i, chunk in enumerate(text_chunks):
            all_chunks.append({
                "text": chunk,
                "source": filename,
                "chunk_id": f"{filename}_{i}"
            })
    return all_chunks