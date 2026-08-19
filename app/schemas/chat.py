from pydantic import BaseModel, Field


class Citation(BaseModel):
    document: str
    page: int | None = None


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=4000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    conversation_id: str
