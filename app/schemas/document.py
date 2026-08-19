from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: str
    chunks_created: int
    status: str


class DocumentSummary(BaseModel):
    document_id: str
    file_name: str
    version: int
    created_at: str
