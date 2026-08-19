from app.core.config import get_settings


def build_context(results: list[dict]) -> tuple[str, list[dict]]:
    """Dedupe, cap chunk count, and label chunks as SOURCE_n for citation."""
    settings = get_settings()

    deduped: list[dict] = []
    seen_chunk_ids = set()
    for r in results:
        if r["chunk_id"] in seen_chunk_ids:
            continue
        seen_chunk_ids.add(r["chunk_id"])
        deduped.append(r)

    top = sorted(deduped, key=lambda r: r["score"], reverse=True)[: settings.context_max_chunks]

    blocks = []
    labeled_sources = []
    for i, chunk in enumerate(top, start=1):
        source_id = f"SOURCE_{i}"
        blocks.append(
            f"[{source_id}]\n"
            f"Document: {chunk['source']}\n"
            f"Page: {chunk['page']}\n"
            f"Text:\n{chunk['text']}"
        )
        labeled_sources.append({**chunk, "source_id": source_id})

    return "\n\n".join(blocks), labeled_sources
