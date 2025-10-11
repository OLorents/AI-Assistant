"""LLM client factory."""

from .interfaces import LLMClient
from .gemini_client import GeminiClient
from .openai_client import OpenAIClient
from .stub_client import StubClient
from ..config.params import AiParameters


class LLMClientFactory:
    @staticmethod
    def create(params: AiParameters) -> LLMClient:
        """Return appropriate LLM client based on provider and API key."""
        api_key = (params.api_key or "").strip()

        if params.provider == "gemini" and api_key:
            return GeminiClient(params.model, api_key)
        if params.provider == "openai" and api_key:
            return OpenAIClient(params.model, api_key)

        # Fallback to stub if key missing or whitespace
        return StubClient(params.model)
