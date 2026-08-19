from pathlib import Path

import pymupdf as fitz

from app.core.constants import SUPPORTED_EXTENSIONS


def load_document(file_path: str) -> list[dict]:
    """Parse a PDF/TXT/MD file into a list of page dicts: page_number, text, source."""
    path = Path(file_path)
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}")

    if ext == ".pdf":
        return _load_pdf(path)
    return _load_text(path)


def _load_pdf(path: Path) -> list[dict]:
    pages = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if not text or not text.strip():
                continue
            pages.append({"page_number": i, "text": text, "source": path.name})
    return pages


def _load_text(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return []
    return [{"page_number": 1, "text": text, "source": path.name}]
