from datetime import datetime, timezone
from typing import Iterable

from app.storage.sqlite import db_session


def get_document_by_hash(file_hash: str) -> dict | None:
    with db_session() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE file_hash = ?", (file_hash,)
        ).fetchone()
        return dict(row) if row else None


def insert_document(document_id: str, file_name: str, file_hash: str, version: int) -> None:
    with db_session() as conn:
        conn.execute(
            "INSERT INTO documents (document_id, file_name, file_hash, version, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (document_id, file_name, file_hash, version, datetime.now(timezone.utc).isoformat()),
        )


def insert_chunks(chunks: Iterable) -> None:
    rows = [(c.chunk_id, c.document_id, c.page_number, c.section, c.text) for c in chunks]
    if not rows:
        return
    with db_session() as conn:
        conn.executemany(
            "INSERT INTO chunks (chunk_id, document_id, page_number, section, text) "
            "VALUES (?, ?, ?, ?, ?)",
            rows,
        )


def get_chunks_by_ids(chunk_ids: list[str]) -> dict[str, dict]:
    if not chunk_ids:
        return {}
    with db_session() as conn:
        placeholders = ",".join("?" for _ in chunk_ids)
        rows = conn.execute(
            "SELECT c.chunk_id, c.page_number, c.section, c.text, c.document_id, "
            "d.file_name, d.version "
            "FROM chunks c JOIN documents d ON c.document_id = d.document_id "
            f"WHERE c.chunk_id IN ({placeholders})",
            chunk_ids,
        ).fetchall()
        return {row["chunk_id"]: dict(row) for row in rows}


def list_documents() -> list[dict]:
    with db_session() as conn:
        rows = conn.execute(
            "SELECT document_id, file_name, version, created_at FROM documents "
            "ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
