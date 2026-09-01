from app.core.config import get_settings
from app.embeddings.model import get_embedding_service
from app.storage.session_store import get_or_create_session


def session_vector_search(session_id: str, query: str, top_k: int | None = None) -> list[dict]:
    settings = get_settings()
    top_k = top_k or settings.vector_top_k

    embedder = get_embedding_service()
    query_vector = embedder.embed_query(query)

    store = get_or_create_session(session_id)
    raw_results = store.search(query_vector, top_k)
    if not raw_results:
        return []

    results = []
    for chunk_id, score in raw_results:
        meta = store.get_chunk(chunk_id)
        if not meta:
            continue
        results.append(
            {
                "chunk_id": chunk_id,
                "score": score,
                "text": meta["text"],
                "source": meta["source"],
                "page": meta["page"],
                "section": meta.get("section"),
            }
        )
    return results
