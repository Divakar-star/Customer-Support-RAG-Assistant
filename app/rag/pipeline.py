import uuid

from app.core.config import get_settings
from app.core.constants import UNSUPPORTED_ANSWER
from app.rag.citations import validate_citations
from app.rag.context_builder import build_context
from app.rag.generator import get_llm_client
from app.rag.prompts import SYSTEM_PROMPT, build_user_message
from app.retrieval.vector_search import vector_search


def answer_question(question: str, conversation_id: str | None = None) -> dict:
    settings = get_settings()
    conversation_id = conversation_id or str(uuid.uuid4())
    question = question.strip()

    results = vector_search(question)

    if not results or results[0]["score"] < settings.retrieval_threshold:
        return _unsupported(conversation_id)

    context_text, labeled_sources = build_context(results)

    llm = get_llm_client()
    raw_answer = llm.generate(SYSTEM_PROMPT, build_user_message(question, context_text))

    answer, citations = validate_citations(raw_answer, labeled_sources)

    if not citations and UNSUPPORTED_ANSWER not in answer:
        # The model didn't ground its answer in any supplied source - refuse
        # rather than present an uncited claim as a policy answer.
        return _unsupported(conversation_id)

    return {"answer": answer, "citations": citations, "conversation_id": conversation_id}


def _unsupported(conversation_id: str) -> dict:
    return {"answer": UNSUPPORTED_ANSWER, "citations": [], "conversation_id": conversation_id}
