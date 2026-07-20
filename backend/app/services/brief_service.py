import asyncio
import logging
import uuid
from datetime import UTC, datetime

import httpx
import sentry_sdk
from fastapi import Depends
from pydantic import ValidationError

from app.core.errors import SAFE_ERRORS
from app.core.exceptions import BriefInputValidationError, BriefNotFoundError
from app.core.providers import LLMProvider, get_llm_provider
from app.core.validations import validate_brief_text
from app.models.brief import Brief
from app.repositories import BriefRepository, get_brief_repository
from app.schemas.api import BriefRequest, BriefStatus, BriefUpdate

logger = logging.getLogger("app.services.brief")


def _map_exception(e: Exception) -> str:
    """Maps various exceptions (httpx, asyncio, validation, etc.) to standardized error codes."""
    if isinstance(e, ValidationError):
        return "ValidationError"

    if isinstance(e, BriefInputValidationError | ValueError):
        return "InputValidationError"

    if isinstance(e, asyncio.TimeoutError | TimeoutError | httpx.TimeoutException):
        return "TimeoutError"

    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status in (401, 403):
            return "AuthenticationError"
        if status == 429:
            return "RateLimitError"
        if status >= 500:
            return "InternalServerError"

    if isinstance(e, httpx.RequestError):
        return "APIConnectionError"

    return e.__class__.__name__


class BriefService:
    """Service to coordinate brief analysis and database persistence."""

    def __init__(self, repo: BriefRepository, provider: LLMProvider) -> None:
        self.repo = repo
        self.provider = provider

    async def create_brief(self, request: BriefRequest) -> Brief:
        """Creates a new brief decoding run in the database with a pending status."""
        async with self.repo as r:
            return await r.create(request.text)

    async def decode_and_update_brief(self, brief_id: uuid.UUID) -> Brief:
        """Calls the LLM provider to analyze the brief and updates the run status in the DB."""
        # 1. Fetch from repository to get input text
        async with self.repo as r:
            db_brief = await r.get(brief_id)
            if not db_brief:
                raise BriefNotFoundError(brief_id)
            input_text = db_brief.input_text

        # 2. Update status to 'processing' and set started_at timing
        async with self.repo as r:
            await r.update(
                brief_id,
                BriefUpdate(
                    status=BriefStatus.PROCESSING,
                    started_at=datetime.now(UTC),
                ),
            )

        # 3. Perform LLM call (retry/timeout logic is handled by the provider decorator)
        logger.info(f"Starting LLM analysis for Brief ID: {brief_id}")
        try:
            validated_text = validate_brief_text(input_text)
            analysis = await self.provider.analyze_brief(validated_text)
            logger.info(f"Brief ID: {brief_id} completed successfully.")
            update_data = BriefUpdate(
                status=BriefStatus.COMPLETED,
                structured_result=analysis,
                raw_provider_output=analysis.model_dump_json(),
                finished_at=datetime.now(UTC),
                error_code=None,
                error_message=None,
            )
        except Exception as e:
            error_code = _map_exception(e)
            error_msg = str(e)

            logger.error(f"Brief ID: {brief_id} failed. Error: {error_code} - {error_msg}")
            sentry_sdk.capture_exception(e)

            safe_msg = SAFE_ERRORS.get(error_code, SAFE_ERRORS["UnknownError"])
            update_data = BriefUpdate(
                status=BriefStatus.FAILED,
                error_code=error_code,
                error_message=safe_msg,
                finished_at=datetime.now(UTC),
                structured_result=None,
                raw_provider_output=None,
            )

        # 4. Save results or error log to the database
        async with self.repo as r:
            return await r.update(brief_id, update_data)

    async def get_brief(self, brief_id: uuid.UUID) -> Brief | None:
        """Retrieves a brief run from the database by its ID."""
        async with self.repo as r:
            return await r.get(brief_id)


def get_brief_service(
    repo: BriefRepository = Depends(get_brief_repository),
    provider: LLMProvider = Depends(get_llm_provider),
) -> BriefService:
    """Factory dependency to instantiate BriefService with its repository and provider."""
    return BriefService(repo, provider)
