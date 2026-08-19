# Enterprise Support RAG Assistant — Phase 1 MVP

A low-cost RAG assistant for Acme Support policy documents: local embeddings + FAISS
semantic search + Google Gemini (free tier) for grounded, cited answers. Refuses to
answer questions the documents don't support.

This is **Phase 1** of the full design in `task.md` — the simplest version that works
end to end. Hybrid (BM25) retrieval, reranking, caching, conversation memory,
evaluation harness, Docker, and auth are deliberately deferred to later rounds; see
`task.md` §75 for the full roadmap.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env          # Windows
# cp .env.example .env          # Mac/Linux
# then edit .env and set GEMINI_API_KEY (https://aistudio.google.com/apikey)
```

## Add sample knowledge

See `docs/sample-documents-brief.md` for what the 8 Acme Support policy documents
should contain. Generate them (Markdown) and drop them in `data/raw/`, then:

```bash
python scripts/ingest_documents.py
```

This chunks, embeds, and indexes every file in `data/raw/` into FAISS + SQLite
(`data/app.db`). Re-running is safe — files already ingested (by content hash) are
skipped.

## Run

```bash
# Terminal 1: API
uvicorn app.main:app --reload

# Terminal 2: UI
streamlit run ui/streamlit_app.py
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Chat UI: http://localhost:8501

## API quick reference

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"How long do refunds take?\"}"
```

```bash
curl -F "file=@data/raw/refund_policy.md" http://localhost:8000/api/v1/documents
```

## How it works

```
Question → embed → FAISS top-K → confidence threshold
                                       ├── too low → "I don't know based on the
                                       │              available company documents."
                                       └── strong enough → build context (top N chunks,
                                            deduped, labeled SOURCE_1..N) → Gemini →
                                            strip any citation not in context → answer
```

## What's not built yet (by design)

BM25/hybrid retrieval + RRF, reranking, metadata filtering, conversation memory,
query rewriting, caching, structured logging, pytest suite, evaluation harness,
Docker, API-key auth, rate limiting, PII masking. These are round-2+ additions on
top of this working core — see `task.md` for the full spec.
