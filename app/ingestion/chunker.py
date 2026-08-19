from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    file_name: str
    page_number: int
    section: str | None
    text: str
    document_version: int


def chunk_page(
    document_id: str,
    file_name: str,
    page_number: int,
    text: str,
    document_version: int = 1,
    chunk_size_tokens: int = 550,
    overlap_tokens: int = 80,
) -> list[Chunk]:
    """Paragraph-based chunking with word-count as a token approximation.

    Chunks are built by accumulating whole paragraphs (as produced by
    ``cleaner.clean_text``) so bullets/policy sentences are never cut mid-line.
    Deterministic: same input + same config always yields the same chunk_ids.
    """
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    chunks: list[Chunk] = []
    current_words: list[str] = []
    current_section: str | None = None
    chunk_number = 0

    def flush() -> None:
        nonlocal current_words, chunk_number
        if not current_words:
            return
        chunk_number += 1
        chunks.append(
            Chunk(
                chunk_id=f"{document_id}_p{page_number}_c{chunk_number}",
                document_id=document_id,
                file_name=file_name,
                page_number=page_number,
                section=current_section,
                text=" ".join(current_words),
                document_version=document_version,
            )
        )
        current_words = (
            current_words[-overlap_tokens:]
            if overlap_tokens < len(current_words)
            else []
        )

    for para in paragraphs:
        if _looks_like_heading(para):
            current_section = para.strip()

        words = para.split()
        if current_words and len(current_words) + len(words) > chunk_size_tokens:
            flush()
        current_words.extend(words)
        if len(current_words) >= chunk_size_tokens:
            flush()

    flush()
    return chunks


def _looks_like_heading(paragraph: str) -> bool:
    line = paragraph.strip()
    if not line:
        return False
    word_count = len(line.split())
    return word_count <= 8 and not line.endswith((".", ",", ";"))
