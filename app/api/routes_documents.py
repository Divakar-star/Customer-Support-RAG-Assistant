import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import get_settings
from app.core.constants import SUPPORTED_EXTENSIONS
from app.ingestion.pipeline import ingest_file
from app.schemas.document import DocumentSummary, DocumentUploadResponse
from app.storage.document_repository import list_documents

router = APIRouter(prefix="/api/v1", tags=["documents"])


@router.post("/documents", response_model=DocumentUploadResponse)
def upload_document(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={"code": "UNSUPPORTED_FILE_TYPE", "message": f"Unsupported file type: {ext}"},
        )

    settings = get_settings()
    raw_dir = Path(settings.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Strip any directory components from the client filename and prefix a
    # random id to prevent path traversal and filename collisions.
    original_name = Path(file.filename).name
    safe_name = f"{uuid.uuid4().hex[:8]}_{original_name}"
    dest_path = raw_dir / safe_name

    with dest_path.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    try:
        return ingest_file(str(dest_path), display_name=original_name)
    except Exception:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "DOCUMENT_PROCESSING_FAILED",
                "message": "The document could not be processed.",
            },
        )


@router.get("/documents", response_model=list[DocumentSummary])
def get_documents():
    return list_documents()
