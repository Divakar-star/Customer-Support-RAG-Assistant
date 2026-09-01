from pydantic import BaseModel, Field

from app.schemas.chat import Citation


class SessionChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=4000)
    conversation_id: str | None = None


class SessionChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    conversation_id: str


class SessionDocumentUploadResponse(BaseModel):
    document_id: str
    chunks_created: int
    status: str


class SessionDocumentSummary(BaseModel):
    file_name: str
    chunks: int
