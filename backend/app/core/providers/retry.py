import asyncio
import logging

from pydantic import ValidationError

from app.core.providers.base import LLMProvider
from app.schemas.api import BriefAnalysisResponse

logger = logging.getLogger("app.providers.retry")


class RetryingLLMProvider(LLMProvider):
    """Decorator to wrap any LLMProvider and add automatic retries with linear backoff."""

    def __init__(self, base_provider: LLMProvider, max_attempts: int, timeout: float) -> None:
        self.base_provider = base_provider
        self.max_attempts = max_attempts
        self.timeout = timeout

    async def analyze_brief(self, text: str) -> BriefAnalysisResponse:
        """Calls the underlying provider with configured timeout and linear retry logic."""
        for attempt in range(1, self.max_attempts + 1):
            try:
                # Wrap the core call in asyncio.wait_for
                return await asyncio.wait_for(
                    self.base_provider.analyze_brief(text),
                    timeout=self.timeout,
                )
            except (TimeoutError, Exception) as e:
                current_err_code = e.__class__.__name__
                if isinstance(e, asyncio.TimeoutError):
                    current_err_code = "TimeoutError"

                # Do not retry on validation errors (or if this is the final attempt)
                is_retriable = not isinstance(e, ValidationError)

                if not is_retriable or attempt == self.max_attempts:
                    logger.error(
                        "LLM analysis failed permanently after %d attempts. Error: %s - %s",
                        attempt,
                        current_err_code,
                        e,
                    )
                    raise

                delay = attempt  # Linear backoff delay: 1s, 2s, etc.
                logger.warning(
                    "LLM analysis attempt %d failed with %s: %s. Retrying in %ds...",
                    attempt,
                    current_err_code,
                    e,
                    delay,
                )
                await asyncio.sleep(delay)

        # Fallback in case loop terminates without raising
        # (though code above always raises or returns)
        raise RuntimeError("Retries exhausted without success")
