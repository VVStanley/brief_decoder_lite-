import asyncio
import logging

from pydantic import ValidationError
from tenacity import (
    AsyncRetrying,
    before_sleep_log,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.providers.base import LLMProvider
from app.schemas.api import BriefAnalysisResponse

logger = logging.getLogger("app.providers.retry")


class RetryingLLMProvider(LLMProvider):
    """Decorator to wrap any LLMProvider and add automatic retries using tenacity."""

    def __init__(self, base_provider: LLMProvider, max_attempts: int, timeout: float) -> None:
        self.base_provider = base_provider
        self.max_attempts = max_attempts
        self.timeout = timeout

    async def analyze_brief(self, text: str) -> BriefAnalysisResponse:
        """Calls the underlying provider with timeout and retry backoff via tenacity."""
        retrying = AsyncRetrying(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((ValidationError, TimeoutError, asyncio.TimeoutError)),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )
        async for attempt in retrying:
            with attempt:
                return await asyncio.wait_for(
                    self.base_provider.analyze_brief(text),
                    timeout=self.timeout,
                )
        raise RuntimeError("Retries exhausted without success")
