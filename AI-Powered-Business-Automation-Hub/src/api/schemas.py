"""API request and response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ..integration_models import IntegrationResult
from ..analytics import (
    IntegrationAnalytics,
    OverviewAnalytics,
    PerformanceAnalytics,
    RecentActivity,
)
from ..models import (
    AutomationAction,
    AutomationExecutionResult,
    TaskAnalysis,
    ProcessingMetadata,
)


class TaskCreateRequest(BaseModel):
    """Request body for creating one API task."""

    task_id: str | None = Field(default=None, min_length=1)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source: str = Field(default="api", min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Structured response for a processed task."""

    task_id: str
    source: str
    analysis: TaskAnalysis | None = None
    planned_actions: list[AutomationAction] = Field(default_factory=list)
    execution_results: list[AutomationAction] = Field(default_factory=list)
    integration_results: list[IntegrationResult] = Field(default_factory=list)
    final_status: str
    processing_metadata: ProcessingMetadata = Field(default_factory=ProcessingMetadata)
    error: str | None = None


class StoredTaskResponse(TaskResponse):
    """Response for a task reconstructed from persisted data."""

    title: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class BatchTaskResponse(BaseModel):
    """Response containing results for sequential batch processing."""

    results: list[TaskResponse]


class HealthResponse(BaseModel):
    """Health endpoint response."""

    status: str
    service: str


class ErrorResponse(BaseModel):
    """Consistent application error response."""

    error: str
    detail: str


class RecentActivityResponse(BaseModel):
    """Recent activity response wrapper."""

    items: list[RecentActivity]


# Keep the internal execution model import visible for API consumers without
# duplicating its fields in the public response schemas.
__all__ = [
    "AutomationExecutionResult",
    "BatchTaskResponse",
    "ErrorResponse",
    "HealthResponse",
    "StoredTaskResponse",
    "TaskCreateRequest",
    "TaskResponse",
    "IntegrationAnalytics",
    "OverviewAnalytics",
    "PerformanceAnalytics",
    "RecentActivityResponse",
]
