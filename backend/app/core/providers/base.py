from typing import Protocol

from app.schemas import BriefAnalysisResponse


class LLMProvider(Protocol):
    """Protocol defining the interface for all LLM providers."""

    async def analyze_brief(self, text: str) -> BriefAnalysisResponse:
        """Asynchronously parses the raw text of a brief.

        Args:
            text: Raw text of the client brief.

        Returns:
            BriefAnalysisResponse: Structured analysis output.
        """
        ...
