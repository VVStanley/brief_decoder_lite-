from typing import Any, cast

from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

from app.core.config import settings
from app.core.providers.base import LLMProvider
from app.core.providers.prompts import SYSTEM_PROMPT
from app.schemas import BriefAnalysisResponse


class GeminiLLMProvider(LLMProvider):
    """Real LLM provider using Google Gemini and PydanticAI."""

    def __init__(self) -> None:
        self.model = GeminiModel(
            cast(Any, settings.GEMINI_MODEL),
            api_key=settings.GEMINI_API_KEY,
        )
        self.agent = Agent(
            self.model,
            result_type=BriefAnalysisResponse,
            system_prompt=SYSTEM_PROMPT,
        )

    async def analyze_brief(self, text: str) -> BriefAnalysisResponse:
        result = await self.agent.run(text)
        return result.data
