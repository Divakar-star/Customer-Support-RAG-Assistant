from fastapi import APIRouter, HTTPException

from app.rag.pipeline import answer_question
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        return answer_question(request.question, request.conversation_id)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503, detail={"code": "LLM_UNAVAILABLE", "message": str(exc)}
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"code": "CHAT_FAILED", "message": "Could not generate an answer."},
        )
