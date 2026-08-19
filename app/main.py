from fastapi import FastAPI

from app.api.routes_chat import router as chat_router
from app.api.routes_documents import router as documents_router
from app.api.routes_health import router as health_router
from app.core.logging import setup_logging
from app.storage.sqlite import init_db

setup_logging()
init_db()

app = FastAPI(title="Enterprise Support RAG Assistant", version="0.1.0")

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(documents_router)
