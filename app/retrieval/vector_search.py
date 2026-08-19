from app.core.config import get_settings
from app.embeddings.model import get_embedding_service
from app.storage.document_repository import get_chunks_by_ids
from app.storage.faiss_store import get_faiss_store


def vector_search(query: str, top_k: int | None = None) -> list[dict]:
    settings = get_settings()
    top_k = top_k or settings.vector_top_k

    embedder = get_embedding_service()
    query_vector = embedder.embed_query(query)

    store = get_faiss_store()
    raw_results = store.search(query_vector, top_k)
    if not raw_results:
        return []

    metadata = get_chunks_by_ids([chunk_id for chunk_id, _ in raw_results])

    results = []
    for chunk_id, score in raw_results:
        meta = metadata.get(chunk_id)
        if not meta:
            continue
        results.append(
            {
                "chunk_id": chunk_id,
                "score": score,
                "text": meta["text"],
                "source": meta["file_name"],
                "page": meta["page_number"],
                "section": meta.get("section"),
            }
        )
    return results
