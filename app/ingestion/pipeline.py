import hashlib
from pathlib import Path

from app.core.constants import SUPPORTED_EXTENSIONS
from app.embeddings.model import get_embedding_service
from app.ingestion.chunker import chunk_page
from app.ingestion.cleaner import clean_text
from app.ingestion.loader import load_document
from app.storage.document_repository import get_document_by_hash, insert_chunks, insert_document
from app.storage.faiss_store import get_faiss_store


def ingest_file(file_path: str, display_name: str | None = None) -> dict:
    path = Path(file_path)
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {path.suffix}")

    # display_name is the human-facing name (shown in citations); it can differ
    # from the on-disk filename, which may carry a uniqueness prefix.
    display_name = display_name or path.name

    file_hash = _hash_file(path)
    existing = get_document_by_hash(file_hash)
    if existing:
        return {
            "document_id": existing["document_id"],
            "chunks_created": 0,
            "status": "duplicate_skipped",
        }

    document_id = f"{_slugify(display_name)}_v1"
    version = 1
    pages = load_document(str(path))

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
                document_version=version,
            )
        )

    if not all_chunks:
        return {"document_id": document_id, "chunks_created": 0, "status": "empty_document"}

    embedder = get_embedding_service()
    vectors = embedder.embed_documents([c.text for c in all_chunks])

    insert_document(document_id, display_name, file_hash, version)
    insert_chunks(all_chunks)

    store = get_faiss_store()
    store.add(vectors, [c.chunk_id for c in all_chunks])

    return {"document_id": document_id, "chunks_created": len(all_chunks), "status": "indexed"}


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _slugify(name: str) -> str:
    stem = Path(name).stem.lower()
    return "".join(c if c.isalnum() else "_" for c in stem).strip("_")
