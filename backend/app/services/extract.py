from pathlib import Path
from docx import Document as DocxDocument
from pypdf import PdfReader

def extract_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    try:
        if p.suffix.lower() == ".pdf":
            reader = PdfReader(str(p))
            return "\n".join(page.extract_text() or "" for page in reader.pages)[:20000]
        if p.suffix.lower() in [".docx", ".doc"]:
            doc = DocxDocument(str(p))
            return "\n".join(par.text for par in doc.paragraphs)[:20000]
        if p.suffix.lower() in [".txt", ".md"]:
            return p.read_text(errors="ignore")[:20000]
    except Exception as exc:
        return f"Could not extract text: {exc}"
    return ""
