import uuid

from app.core.config import get_settings
from app.core.constants import NO_SESSION_DOCS, SESSION_UNSUPPORTED_ANSWER
from app.rag.citations import validate_citations
from app.rag.context_builder import build_context
from app.rag.generator import get_llm_client
from app.rag.prompts import SESSION_SYSTEM_PROMPT, build_user_message
from app.retrieval.session_search import session_vector_search
from app.storage.session_store import SessionKnowledgeStore, get_or_create_session

_SUMMARY_INTENT_PHRASES = (
    "summary",
    "summarize",
    "summarise",
    "overview",
    "explain this document",
    "explain the document",
    "explain this file",
    "explain the file",
    "what is this document about",
    "what is this file about",
    "what's this document about",
    "what's this file about",
    "tell me about this document",
    "tell me about this file",
    "tell me about the document",
    "tell me about the file",
    "about this document",
    "about the file",
    "about this file",
)


def _is_summary_intent(question: str) -> bool:
    q = question.lower()
    return any(phrase in q for phrase in _SUMMARY_INTENT_PHRASES)


def _select_context(
    session_id: str, store: SessionKnowledgeStore, question: str, settings
) -> list[dict] | None:
    """Picks which chunks to answer from. Returns None if nothing qualifies
    (caller should refuse).

    A pure similarity score doesn't mean much for a vague question ("summarize
    this") or a document that's small enough to hand over in full anyway - in
    both cases we skip the score gate and just use the document's own chunk
    order instead of ranking by relevance.
    """
    total_chunks = store.total_chunks()

    if total_chunks <= settings.context_max_chunks:
        return store.get_ordered_chunks(total_chunks)

    if _is_summary_intent(question):
        return store.get_ordered_chunks(settings.context_max_chunks)

    results = session_vector_search(session_id, question)
    if not results or results[0]["score"] < settings.retrieval_threshold:
        return None
    return results


def answer_session_question(
    session_id: str, question: str, conversation_id: str | None = None
) -> dict:
    settings = get_settings()
    conversation_id = conversation_id or str(uuid.uuid4())
    question = question.strip()

    store = get_or_create_session(session_id)
    if not store.has_documents():
        return _refusal(NO_SESSION_DOCS, conversation_id)

    results = _select_context(session_id, store, question, settings)
    if results is None:
        return _refusal(SESSION_UNSUPPORTED_ANSWER, conversation_id)

    context_text, labeled_sources = build_context(results)

    llm = get_llm_client()
    raw_answer = llm.generate(SESSION_SYSTEM_PROMPT, build_user_message(question, context_text))

    answer, citations = validate_citations(raw_answer, labeled_sources)

    if not citations and SESSION_UNSUPPORTED_ANSWER not in answer:
        # The model didn't ground its answer in any supplied source - refuse
        # rather than present an uncited claim as fact.
        return _refusal(SESSION_UNSUPPORTED_ANSWER, conversation_id)

    return {"answer": answer, "citations": citations, "conversation_id": conversation_id}


def _refusal(message: str, conversation_id: str) -> dict:
    return {"answer": message, "citations": [], "conversation_id": conversation_id}
