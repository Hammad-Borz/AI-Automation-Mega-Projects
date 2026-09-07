"""Pydantic models for the initial automation domain."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .integration_models import IntegrationResult


class WorkflowStatus(str, Enum):
    """Statuses returned by the Phase 1 workflow."""

    COMPLETED = "completed"
    FAILED = "failed"


class TaskLifecycle(str, Enum):
    """Persisted lifecycle state for a task."""

    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingMetadata(BaseModel):
    """Timing and lifecycle information for one processing attempt."""

    lifecycle_status: TaskLifecycle = TaskLifecycle.RECEIVED
    processing_started_at: datetime | None = None
    processing_completed_at: datetime | None = None
    processing_duration_ms: float | None = Field(default=None, ge=0.0)
    failure_message: str | None = None


class TaskCategory(str, Enum):
    """Business category assigned during task analysis."""

    SUPPORT = "support"
    SALES = "sales"
    URGENT = "urgent"
    BILLING = "billing"
    OPERATIONS = "operations"
    GENERAL = "general"


class TaskPriority(str, Enum):
    """Priority assigned during task analysis."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskAnalysis(BaseModel):
    """Structured, provider-independent analysis of a business task."""

    category: TaskCategory
    priority: TaskPriority
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_actions: list[str] = Field(default_factory=list)


class ActionStatus(str, Enum):
    """Lifecycle status for a planned automation action."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AutomationAction(BaseModel):
    """A single planned or executed local automation action."""

    action_id: str
    action_type: str
    description: str
    status: ActionStatus = ActionStatus.PENDING
    metadata: dict[str, Any] = Field(default_factory=dict)


class AutomationExecutionResult(BaseModel):
    """Structured outcome for all actions executed for one task."""

    task_id: str
    actions: list[AutomationAction] = Field(default_factory=list)
    successful_actions: list[str] = Field(default_factory=list)
    failed_actions: list[str] = Field(default_factory=list)
    overall_status: ActionStatus = ActionStatus.COMPLETED
    integration_results: list[IntegrationResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BusinessTask(BaseModel):
    """A business request entering the automation workflow."""

    task_id: str
    source: str
    title: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AutomationResult(BaseModel):
    """The outcome of processing a business task."""

    task_id: str
    status: WorkflowStatus
    message: str
    actions: list[str] = Field(default_factory=list)
    analysis: TaskAnalysis | None = None
    planned_actions: list[AutomationAction] = Field(default_factory=list)
    execution_result: AutomationExecutionResult | None = None
    processing_metadata: ProcessingMetadata = Field(default_factory=ProcessingMetadata)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
