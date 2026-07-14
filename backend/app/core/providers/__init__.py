from app.core.config import settings
from app.core.providers.base import LLMProvider
from app.core.providers.fake import FakeLLMProvider
from app.core.providers.gemini import GeminiLLMProvider
from app.core.providers.retry import RetryingLLMProvider


def get_llm_provider() -> LLMProvider:
    """Factory function to instantiate the configured LLM provider."""
    provider_name = settings.LLM_PROVIDER.lower()
    if provider_name == "gemini":
        base_provider: LLMProvider = GeminiLLMProvider()
    else:
        base_provider = FakeLLMProvider()

    return RetryingLLMProvider(
        base_provider=base_provider,
        max_attempts=settings.LLM_MAX_ATTEMPTS,
        timeout=settings.LLM_TIMEOUT,
    )


__all__ = [
    "LLMProvider",
    "FakeLLMProvider",
    "GeminiLLMProvider",
    "RetryingLLMProvider",
    "get_llm_provider",
]
