from typing import Any, Protocol

from pydantic_ai import Agent

from app.core.providers.prompts import format_correction_prompt
from app.schemas import BriefAnalysisResponse


class LLMProvider(Protocol):
    """Protocol defining the interface for all LLM providers."""

    async def analyze_brief(
        self, text: str, correction_context: str | None = None
    ) -> BriefAnalysisResponse:
        """Asynchronously parses the raw text of a brief.

        Args:
            text: Raw text of the client brief.
            correction_context: Optional description of previous validation error
                for self-correction.

        Returns:
            BriefAnalysisResponse: Structured analysis output.
        """
        ...


class BaseAgentLLMProvider(LLMProvider):
    """Base class for LLM providers backed by a PydanticAI Agent."""

    agent: Agent[Any, BriefAnalysisResponse]

    async def analyze_brief(
        self, text: str, correction_context: str | None = None
    ) -> BriefAnalysisResponse:
        prompt = format_correction_prompt(text, correction_context)
        result = await self.agent.run(prompt)
        return result.data

