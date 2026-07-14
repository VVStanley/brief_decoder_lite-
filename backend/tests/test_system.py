import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.schemas import HealthCheckState


def test_environment_configuration():
    """Ensure Dynaconf loaded the [testing] environment during tests."""
    assert settings.current_env.lower() == "testing"
    assert "brief_decoder_test" in settings.DATABASE_URL


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint returns Status: Ok."""
    response = await client.get("/api/health")
    assert response.status_code == 200

    data = HealthCheckState.model_validate(response.json())
    assert data.status == "Ok"
    assert response.json() == {"Status": "Ok"}
