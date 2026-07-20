import logging
import uuid

import sentry_sdk
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.core.providers import LLMProvider
from app.repositories import get_brief_repository
from app.schemas.api import BriefRequest, BriefResponse
from app.services import BriefService, get_brief_service

logger = logging.getLogger("app.api.v1.briefs")
router = APIRouter(prefix="/briefs", tags=["Briefs"])


async def run_background_brief_decode(brief_id: uuid.UUID, provider: LLMProvider) -> None:
    """Helper background task that executes LLM analysis with a fresh repository context."""
    repo = get_brief_repository()
    try:
        service = get_brief_service(repo, provider)
        await service.decode_and_update_brief(brief_id)
    except Exception as e:
        logger.error(f"Background execution failed for brief {brief_id}: {e}", exc_info=True)
        sentry_sdk.capture_exception(e)


@router.post("", response_model=BriefResponse, status_code=202)
async def decode_brief(
    request: BriefRequest,
    background_tasks: BackgroundTasks,
    service: BriefService = Depends(get_brief_service),
) -> BriefResponse:
    """Creates a brief decoding run and triggers the analysis in the background."""
    db_brief = await service.create_brief(request)

    # Enqueue background task
    background_tasks.add_task(run_background_brief_decode, db_brief.id, service.provider)

    return BriefResponse.model_validate(db_brief)


@router.get("/{brief_id}", response_model=BriefResponse)
async def get_brief(
    brief_id: uuid.UUID,
    service: BriefService = Depends(get_brief_service),
) -> BriefResponse:
    """Gets the details and analysis results of a specific brief."""
    db_brief = await service.get_brief(brief_id)
    if not db_brief:
        raise HTTPException(status_code=404, detail="Brief not found")

    return BriefResponse.model_validate(db_brief)
