import asyncio
from typing import cast

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import SAFE_ERRORS
from app.core.providers import (
    FakeLLMProvider,
    LLMProvider,
    RetryingLLMProvider,
    get_llm_provider,
)
from app.schemas.api import BriefAnalysisResponse, BriefRequest, RiskItem, SeverityEnum

# =====================================================================
# 1. Schema Validation Tests
# =====================================================================


def test_request_validation_too_short():
    """Ensure BriefRequest requires text to be at least 10 characters."""
    with pytest.raises(ValidationError):
        BriefRequest(text="Short")


def test_risk_item_invalid_severity():
    """Ensure RiskItem validation fails for invalid severity values."""
    with pytest.raises(ValidationError):
        RiskItem(
            description="Test Risk",
            severity=cast(SeverityEnum, "critical"),  # Not in SeverityEnum
            mitigation="Test Mitigation",
        )


# =====================================================================
# 2. Mock Providers for Testing
# =====================================================================


class ErrorLLMProvider(LLMProvider):
    """LLM provider simulation that always raises an error."""

    async def analyze_brief(self, text: str) -> BriefAnalysisResponse:
        raise RuntimeError("LLM service unavailable")


# =====================================================================
# 3. Integration Tests
# =====================================================================


@pytest.mark.asyncio
async def test_decode_brief_success(client: AsyncClient, app: FastAPI):
    """Test successful brief decoding flow using FakeLLMProvider."""
    # Override provider to use FakeLLMProvider
    app.dependency_overrides[get_llm_provider] = lambda: FakeLLMProvider()

    try:
        # 1. Send decode request
        payload = {"text": "Need a delivery application. Budget is 5k USD. Deadline is 2 months."}
        response = await client.post("/api/v1/briefs", json=payload)
        assert response.status_code == 202

        data = response.json()
        brief_id = data["id"]
        assert data["status"] == "pending"
        assert data["input_text"] == payload["text"]

        # 2. Get status (FastAPI BackgroundTasks run synchronously before client returns in tests)
        get_response = await client.get(f"/api/v1/briefs/{brief_id}")
        assert get_response.status_code == 200

        run_data = get_response.json()
        assert run_data["status"] == "completed"
        assert run_data["structured_result"] is not None
        assert isinstance(run_data["structured_result"]["project_type"], str)
        assert len(run_data["structured_result"]["project_type"]) > 0
        assert len(run_data["structured_result"]["risks"]) > 0
        assert run_data["error_code"] is None
        assert run_data["error_message"] is None
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_decode_brief_failure(client: AsyncClient, app: FastAPI):
    """Test brief decoding failure handling when the LLM provider fails."""
    # Override provider to use ErrorLLMProvider
    app.dependency_overrides[get_llm_provider] = lambda: ErrorLLMProvider()

    try:
        # 1. Send decode request
        payload = {"text": "Some valid project brief text that meets length requirements."}
        response = await client.post("/api/v1/briefs", json=payload)
        assert response.status_code == 202

        data = response.json()
        brief_id = data["id"]
        assert data["status"] == "pending"

        # 2. Get status and check error capturing
        get_response = await client.get(f"/api/v1/briefs/{brief_id}")
        assert get_response.status_code == 200

        run_data = get_response.json()
        assert run_data["status"] == "failed"
        assert run_data["structured_result"] is None
        assert run_data["error_code"] == "RuntimeError"
        assert run_data["error_message"] == SAFE_ERRORS["UnknownError"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_brief_not_found(client: AsyncClient):
    """Ensure requesting a non-existent brief ID returns 404."""
    random_uuid = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/briefs/{random_uuid}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Brief not found"


class FlakyLLMProvider(LLMProvider):
    def __init__(self, fail_count: int) -> None:
        self.fail_count = fail_count
        self.calls = 0

    async def analyze_brief(self, text: str) -> BriefAnalysisResponse:
        self.calls += 1
        if self.calls <= self.fail_count:
            raise RuntimeError("Temporary API issue")
        # Return a valid mock response using FakeLLMProvider
        fake = FakeLLMProvider()
        return await fake.analyze_brief(text)


@pytest.mark.asyncio
async def test_decode_brief_retry_success(client: AsyncClient, app: FastAPI):
    """Test that a brief decoding succeeds if LLM provider fails first but succeeds on retry."""
    flaky_provider = FlakyLLMProvider(fail_count=1)
    app.dependency_overrides[get_llm_provider] = lambda: RetryingLLMProvider(
        base_provider=flaky_provider, max_attempts=3, timeout=45.0
    )

    try:
        payload = {"text": "Some valid project brief text that meets length requirements."}
        response = await client.post("/api/v1/briefs", json=payload)
        assert response.status_code == 202
        brief_id = response.json()["id"]

        # Wait a bit for background tasks (including sleep/retry) to finish
        run_data = {}
        for _ in range(20):
            await asyncio.sleep(0.2)
            get_response = await client.get(f"/api/v1/briefs/{brief_id}")
            run_data = get_response.json()
            if run_data["status"] in ["completed", "failed"]:
                break

        assert run_data["status"] == "completed"
        assert run_data["structured_result"] is not None
        assert run_data["started_at"] is not None
        assert run_data["finished_at"] is not None
        assert flaky_provider.calls == 2  # 1 fail, 1 success
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cleanup_service_zombie_tasks(db_session: AsyncSession):
    """Test that CleanupService fails tasks that are stuck in 'processing' status."""
    from datetime import UTC, datetime, timedelta

    from app.models.brief import Brief
    from app.services.cleanup_service import CleanupService

    # 1. Create a zombie brief manually in the DB
    old_time = datetime.now(UTC) - timedelta(minutes=5)
    zombie = Brief(
        input_text="Test zombie brief text that is long enough.",
        status="processing",
        started_at=old_time,
    )
    db_session.add(zombie)
    await db_session.commit()
    zombie_id = zombie.id

    # 2. Run CleanupService
    await CleanupService.fail_abandoned_briefs(timeout_minutes=3)

    # 3. Retrieve the brief and check state
    from sqlalchemy import select

    db_session.expire_all()
    stmt = select(Brief).where(Brief.id == zombie_id)
    result = await db_session.execute(stmt)
    updated_brief = result.scalar_one()

    assert updated_brief.status == "failed"
    assert updated_brief.error_code == "TaskAbandoned"
    assert updated_brief.error_message == SAFE_ERRORS["TaskAbandoned"]
    assert updated_brief.finished_at is not None
