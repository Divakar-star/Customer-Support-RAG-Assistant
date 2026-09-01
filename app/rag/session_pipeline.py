import uuid

from app.core.config import get_settings
from app.core.constants import NO_SESSION_DOCS, SESSION_UNSUPPORTED_ANSWER
from app.rag.citations import validate_citations
from app.rag.context_builder import build_context
from app.rag.generator import get_llm_client
from app.rag.prompts import SESSION_SYSTEM_PROMPT, build_user_message
from app.retrieval.session_search import session_vector_search
from app.storage.session_store import get_or_create_session


def answer_session_question(
    session_id: str, question: str, conversation_id: str | None = None
) -> dict:
    settings = get_settings()
    conversation_id = conversation_id or str(uuid.uuid4())
    question = question.strip()

    store = get_or_create_session(session_id)
    if not store.has_documents():
        return _refusal(NO_SESSION_DOCS, conversation_id)

    results = session_vector_search(session_id, question)

    if not results or results[0]["score"] < settings.retrieval_threshold:
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
