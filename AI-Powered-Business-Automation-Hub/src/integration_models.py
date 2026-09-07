"""Structured models for simulated and future external integrations."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class IntegrationStatus(str, Enum):
    """Lifecycle status of an integration operation."""

    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    SIMULATED = "simulated"


class IntegrationRequest(BaseModel):
    """Context passed from the router to a connector."""

    integration_name: str
    action_name: str
    task_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IntegrationResult(BaseModel):
    """Outcome returned by an integration connector."""

    integration_name: str
    action_name: str
    task_id: str
    status: IntegrationStatus
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))