import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.core.providers import LLMProvider, get_llm_provider
from app.repositories import BriefRepository, get_brief_repository
from app.schemas.api import BriefRequest, BriefResponse
from app.services.brief_service import BriefService

router = APIRouter(prefix="/briefs", tags=["Briefs"])


async def run_background_brief_decode(brief_id: uuid.UUID, provider: LLMProvider) -> None:
    """Helper background task that executes LLM analysis with a fresh repository context."""
    repo = get_brief_repository()
    try:
        service = BriefService(repo, provider)
        await service.decode_and_update_brief(brief_id)
    except Exception:
        # Silence background execution exceptions to prevent task crashes
        pass


@router.post("", response_model=BriefResponse, status_code=202)
async def decode_brief(
    request: BriefRequest,
    background_tasks: BackgroundTasks,
    repo: BriefRepository = Depends(get_brief_repository),
    provider: LLMProvider = Depends(get_llm_provider),
) -> BriefResponse:
    """Creates a brief decoding run and triggers the analysis in the background."""
    service = BriefService(repo, provider)
    db_brief = await service.create_brief(request)

    # Enqueue background task
    background_tasks.add_task(run_background_brief_decode, db_brief.id, provider)

    return BriefResponse.model_validate(db_brief)


@router.get("/{brief_id}", response_model=BriefResponse)
async def get_brief(
    brief_id: uuid.UUID,
    repo: BriefRepository = Depends(get_brief_repository),
    provider: LLMProvider = Depends(get_llm_provider),
) -> BriefResponse:
    """Gets the details and analysis results of a specific brief."""
    service = BriefService(repo, provider)
    db_brief = await service.get_brief(brief_id)
    if not db_brief:
        raise HTTPException(status_code=404, detail="Brief not found")

    return BriefResponse.model_validate(db_brief)
