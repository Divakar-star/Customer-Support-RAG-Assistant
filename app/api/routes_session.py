from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile

from app.core.constants import SUPPORTED_EXTENSIONS
from app.ingestion.session_pipeline import ingest_file_ephemeral
from app.rag.session_pipeline import answer_session_question
from app.schemas.session import (
    SessionChatRequest,
    SessionChatResponse,
    SessionDocumentSummary,
    SessionDocumentUploadResponse,
)
from app.storage.session_store import clear_session, get_or_create_session

router = APIRouter(prefix="/api/v1/session", tags=["session"])


def session_id_header(x_session_id: str = Header(..., alias="X-Session-Id")) -> str:
    if not x_session_id.strip():
        raise HTTPException(
            status_code=400,
            detail={"code": "MISSING_SESSION_ID", "message": "X-Session-Id header is required."},
        )
    return x_session_id.strip()


@router.post("/documents", response_model=SessionDocumentUploadResponse)
async def upload_session_document(
    file: UploadFile = File(...), session_id: str = Depends(session_id_header)
):
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={"code": "UNSUPPORTED_FILE_TYPE", "message": f"Unsupported file type: {ext}"},
        )

    file_bytes = await file.read()
    store = get_or_create_session(session_id)

    try:
        return ingest_file_ephemeral(file_bytes, file.filename, store)
    except Exception:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "DOCUMENT_PROCESSING_FAILED",
                "message": "The document could not be processed.",
            },
        )


@router.get("/documents", response_model=list[SessionDocumentSummary])
def list_session_documents(session_id: str = Depends(session_id_header)):
    store = get_or_create_session(session_id)
    return store.list_documents()


@router.delete("/documents")
def delete_session_documents(session_id: str = Depends(session_id_header)):
    clear_session(session_id)
    return {"status": "cleared"}


@router.post("/chat", response_model=SessionChatResponse)
def session_chat(request: SessionChatRequest, session_id: str = Depends(session_id_header)):
    try:
        return answer_session_question(session_id, request.question, request.conversation_id)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503, detail={"code": "LLM_UNAVAILABLE", "message": str(exc)}
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={"code": "CHAT_FAILED", "message": "Could not generate an answer."},
        )
