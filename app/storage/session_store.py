import threading

import faiss
import numpy as np

from app.ingestion.chunker import Chunk


class SessionKnowledgeStore:
    """In-memory, per-session vector store. Never touches disk - all data lives
    for the life of the API process and is only reachable via its session_id.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._index: faiss.Index | None = None
        self._chunk_ids: list[str] = []
        self._chunks: dict[str, dict] = {}
        self._file_hashes: set[str] = set()
        self._documents: dict[str, dict] = {}

    def has_file_hash(self, file_hash: str) -> bool:
        with self._lock:
            return file_hash in self._file_hashes

    def add(
        self,
        chunks: list[Chunk],
        vectors: np.ndarray,
        file_hash: str,
        display_name: str,
    ) -> None:
        if not chunks:
            return
        with self._lock:
            if self._index is None:
                self._index = faiss.IndexFlatIP(vectors.shape[1])
            self._index.add(vectors)
            for chunk in chunks:
                self._chunk_ids.append(chunk.chunk_id)
                self._chunks[chunk.chunk_id] = {
                    "text": chunk.text,
                    "source": chunk.file_name,
                    "page": chunk.page_number,
                    "section": chunk.section,
                }
            self._file_hashes.add(file_hash)
            doc = self._documents.setdefault(
                display_name, {"file_name": display_name, "chunks": 0}
            )
            doc["chunks"] += len(chunks)

    def search(self, query_vector: np.ndarray, top_k: int) -> list[tuple[str, float]]:
        with self._lock:
            if self._index is None or self._index.ntotal == 0:
                return []
            query = np.asarray([query_vector], dtype="float32")
            scores, indices = self._index.search(query, min(top_k, self._index.ntotal))
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:
                    continue
                results.append((self._chunk_ids[idx], float(score)))
            return results

    def get_chunk(self, chunk_id: str) -> dict | None:
        with self._lock:
            return self._chunks.get(chunk_id)

    def list_documents(self) -> list[dict]:
        with self._lock:
            return list(self._documents.values())

    def has_documents(self) -> bool:
        with self._lock:
            return bool(self._documents)


_sessions: dict[str, SessionKnowledgeStore] = {}
_registry_lock = threading.Lock()


def get_or_create_session(session_id: str) -> SessionKnowledgeStore:
    with _registry_lock:
        store = _sessions.get(session_id)
        if store is None:
            store = SessionKnowledgeStore()
            _sessions[session_id] = store
        return store


def clear_session(session_id: str) -> None:
    with _registry_lock:
        _sessions.pop(session_id, None)
