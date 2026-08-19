import re

_SOURCE_RE = re.compile(r"\[SOURCE_(\d+)\]")


def extract_cited_source_ids(answer_text: str) -> set[str]:
    return {f"SOURCE_{n}" for n in _SOURCE_RE.findall(answer_text)}


def validate_citations(answer_text: str, labeled_sources: list[dict]) -> tuple[str, list[dict]]:
    """Never trust LLM-produced citations blindly: strip any [SOURCE_n] that
    doesn't exist in the context that was actually supplied.
    """
    valid_ids = {s["source_id"] for s in labeled_sources}
    cited_ids = extract_cited_source_ids(answer_text)

    for bad_id in cited_ids - valid_ids:
        answer_text = answer_text.replace(f"[{bad_id}]", "")

    accepted_ids = cited_ids & valid_ids
    seen = set()
    citations = []
    for s in labeled_sources:
        if s["source_id"] not in accepted_ids:
            continue
        key = (s["source"], s["page"])
        if key in seen:
            continue
        seen.add(key)
        citations.append({"document": s["source"], "page": s["page"]})

    return answer_text.strip(), citations
