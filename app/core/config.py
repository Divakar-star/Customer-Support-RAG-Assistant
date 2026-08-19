from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    data_dir: str = "./data"
    raw_dir: str = "./data/raw"
    sqlite_path: str = "./data/app.db"
    faiss_index_path: str = "./data/indexes/faiss.index"
    faiss_map_path: str = "./data/indexes/chunk_ids.json"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    vector_top_k: int = 10
    context_max_chunks: int = 5
    retrieval_threshold: float = 0.35

    chunk_size_tokens: int = 550
    chunk_overlap_tokens: int = 80

    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    llm_temperature: float = 0.1
    llm_max_output_tokens: int = 500

    log_user_content: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
