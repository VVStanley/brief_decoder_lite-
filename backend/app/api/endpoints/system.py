from fastapi import APIRouter

from app.schemas import HealthCheckState

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthCheckState)
async def health_check() -> HealthCheckState:
    """Health check endpoint to verify backend service status."""
    return HealthCheckState(Status="Ok")
