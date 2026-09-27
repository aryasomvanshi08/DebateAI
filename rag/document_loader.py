import fitz  # PyMuPDF
from pathlib import Path

def load_pdf_text(file_path: str) -> str:
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"No such file: {file_path}")
    doc = fitz.open(file_path)
    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())
    doc.close()
    return "\n".join(pages_text)


def load_documents_from_folder(folder_path: str) -> dict:
    folder = Path(folder_path)
    documents = {}
    for pdf_file in folder.glob("*.pdf"):
        documents[pdf_file.name] = load_pdf_text(str(pdf_file))
    return documents