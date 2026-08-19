import time
from abc import ABC, abstractmethod

from google import genai
from google.genai import errors, types

from app.core.config import get_settings

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 3
_BACKOFF_SECONDS = 1.5


class LLMClient(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_message: str) -> str:
        ...


class GeminiLLMClient(LLMClient):
    """Wraps Google's free-tier Gemini API behind the LLMClient interface so the
    RAG pipeline can swap providers without changing retrieval/prompting logic.
    """

    def __init__(self):
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model
        self._temperature = settings.llm_temperature
        self._max_output_tokens = settings.llm_max_output_tokens

    def generate(self, system_prompt: str, user_message: str) -> str:
        # Google's free tier returns transient 429/5xx under load fairly often -
        # retry those a couple of times; anything else fails immediately.
        last_error: Exception | None = None
        for attempt in range(_MAX_ATTEMPTS):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=self._temperature,
                        max_output_tokens=self._max_output_tokens,
                    ),
                )
                return (response.text or "").strip()
            except errors.APIError as exc:
                last_error = exc
                if exc.code not in _RETRYABLE_STATUS_CODES or attempt == _MAX_ATTEMPTS - 1:
                    raise
                time.sleep(_BACKOFF_SECONDS * (2**attempt))
        raise last_error  # pragma: no cover - unreachable, satisfies type checkers


_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = GeminiLLMClient()
    return _llm_client
