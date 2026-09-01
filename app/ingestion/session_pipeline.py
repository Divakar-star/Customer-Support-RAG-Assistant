import hashlib
import tempfile
from pathlib import Path

from app.core.constants import SUPPORTED_EXTENSIONS
from app.embeddings.model import get_embedding_service
from app.ingestion.chunker import chunk_page
from app.ingestion.cleaner import clean_text
from app.ingestion.loader import load_document
from app.storage.session_store import SessionKnowledgeStore


def ingest_file_ephemeral(
    file_bytes: bytes, display_name: str, session_store: SessionKnowledgeStore
) -> dict:
    ext = Path(display_name).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}")

    file_hash = hashlib.sha256(file_bytes).hexdigest()
    if session_store.has_file_hash(file_hash):
        return {
            "document_id": display_name,
            "chunks_created": 0,
            "status": "duplicate_skipped",
        }

    document_id = display_name

    # Written to a temp dir only so the existing PDF/text loader has a real
    # file path to read; the directory (and file) is deleted immediately
    # after parsing, regardless of outcome.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / f"upload{ext}"
        tmp_path.write_bytes(file_bytes)
        pages = load_document(str(tmp_path))

    all_chunks = []
    for page in pages:
        cleaned = clean_text(page["text"])
        if not cleaned:
            continue
        all_chunks.extend(
            chunk_page(
                document_id=document_id,
                file_name=display_name,
                page_number=page["page_number"],
                text=cleaned,
            )
        )

    if not all_chunks:
        return {"document_id": document_id, "chunks_created": 0, "status": "empty_document"}

    embedder = get_embedding_service()
    vectors = embedder.embed_documents([c.text for c in all_chunks])

    session_store.add(all_chunks, vectors, file_hash, display_name)

    return {"document_id": document_id, "chunks_created": len(all_chunks), "status": "indexed"}
