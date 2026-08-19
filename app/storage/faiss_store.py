import json
from pathlib import Path

import faiss
import numpy as np

from app.core.config import get_settings


class FaissStore:
    def __init__(self):
        settings = get_settings()
        self._index_path = Path(settings.faiss_index_path)
        self._map_path = Path(settings.faiss_map_path)
        self._index: faiss.Index | None = None
        self._chunk_ids: list[str] = []
        self._load()

    def _load(self) -> None:
        if self._index_path.exists() and self._map_path.exists():
            self._index = faiss.read_index(str(self._index_path))
            self._chunk_ids = json.loads(self._map_path.read_text(encoding="utf-8"))

    def _ensure_index(self, dimension: int) -> None:
        if self._index is None:
            self._index = faiss.IndexFlatIP(dimension)

    def add(self, vectors: np.ndarray, chunk_ids: list[str]) -> None:
        if len(vectors) == 0:
            return
        self._ensure_index(vectors.shape[1])
        self._index.add(vectors)
        self._chunk_ids.extend(chunk_ids)
        self._persist()

    def search(self, query_vector: np.ndarray, top_k: int) -> list[tuple[str, float]]:
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

    def _persist(self) -> None:
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(self._index_path))
        self._map_path.write_text(json.dumps(self._chunk_ids), encoding="utf-8")

    @property
    def total_vectors(self) -> int:
        return self._index.ntotal if self._index else 0


_store: FaissStore | None = None


def get_faiss_store() -> FaissStore:
    global _store
    if _store is None:
        _store = FaissStore()
    return _store
