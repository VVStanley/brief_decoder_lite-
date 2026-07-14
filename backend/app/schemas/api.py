import uuid
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthCheckState(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: Literal["Ok"] = Field(..., alias="Status")


class SeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BriefStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskItem(BaseModel):
    description: str = Field(..., description="Description of the identified risk")
    severity: SeverityEnum = Field(..., description="Severity level of the risk")
    mitigation: str = Field(..., description="Suggested way to mitigate or minimize the risk")


class BriefAnalysisResponse(BaseModel):
    """The structured output format returned by the AI provider."""

    project_type: str = Field(..., description="Main type or domain of the project")
    budget_info: str | None = Field(
        None,
        description="Budget description, limits, or constraints mentioned in the brief",
    )
    deadline_info: str | None = Field(
        None,
        description="Deadline, milestones, or timeline constraints mentioned in the brief",
    )
    key_requirements: list[str] = Field(
        default_factory=list,
        description="List of key requirements extracted from the brief",
    )
    risks: list[RiskItem] = Field(
        default_factory=list,
        description="List of identified risks with their severity and mitigation strategies",
    )


class BriefRequest(BaseModel):
    """Input payload for a brief analysis request."""

    text: str = Field(
        ...,
        min_length=10,
        description="Raw brief text to analyze",
        examples=[
            "We need a mobile app for food delivery. Budget is 15k USD. Deadline: 3 months."
        ],
    )


class BriefUpdate(BaseModel):
    """Payload to update an existing Brief analysis."""

    status: BriefStatus
    structured_result: BriefAnalysisResponse | None = None
    raw_provider_output: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class BriefResponse(BaseModel):
    """Output details of a brief analysis."""

    id: uuid.UUID
    status: BriefStatus
    input_text: str
    structured_result: BriefAnalysisResponse | None = None
    error_code: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
