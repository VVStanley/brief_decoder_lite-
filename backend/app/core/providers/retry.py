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
                return await asyncio.wait_for(
                    self.base_provider.analyze_brief(text),
                    timeout=self.timeout,
                )
            except ValidationError as e:
                if attempt == self.max_attempts:
                    logger.error(
                        "LLM schema validation failed permanently after %d attempts: %s",
                        attempt,
                        e,
                    )
                    raise
                logger.warning("LLM attempt %d failed with ValidationError. Retrying...", attempt)

            except TimeoutError:
                if attempt == self.max_attempts:
                    logger.error("LLM timeout permanently after %d attempts.", attempt)
                    raise
                logger.warning("LLM attempt %d failed with TimeoutError. Retrying...", attempt)

            except Exception as e:
                logger.error("LLM analysis failed permanently with non-retriable error: %s", e)
                raise

            await asyncio.sleep(attempt)

        raise RuntimeError("Retries exhausted without success")
