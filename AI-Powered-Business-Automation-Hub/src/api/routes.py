"""Thin FastAPI routes over the existing automation workflow."""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from ..database_manager import DatabaseManager
from ..analytics import AnalyticsService
from ..exceptions import DuplicateTaskError, WorkflowError
from ..models import BusinessTask, WorkflowStatus
from ..workflow import Workflow
from .dependencies import get_analytics_service, get_database_manager, get_workflow
from .schemas import (
    BatchTaskResponse,
    HealthResponse,
    StoredTaskResponse,
    TaskCreateRequest,
    TaskResponse,
    RecentActivityResponse,
    OverviewAnalytics,
    PerformanceAnalytics,
    IntegrationAnalytics,
)

router = APIRouter()

_SERVICE_NAME = "AI-Powered Business Automation Hub"


@router.get("/analytics/overview", response_model=OverviewAnalytics, summary="Get task overview analytics")
def analytics_overview(
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> OverviewAnalytics:
    """Return task counts and grouped operational metrics."""
    return analytics.overview()


@router.get("/analytics/performance", response_model=PerformanceAnalytics, summary="Get processing performance")
def analytics_performance(
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> PerformanceAnalytics:
    """Return persisted processing duration metrics in seconds."""
    return analytics.performance()


@router.get("/analytics/integrations", response_model=IntegrationAnalytics, summary="Get integration analytics")
def analytics_integrations(
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> IntegrationAnalytics:
    """Return counts for persisted integration result events."""
    return analytics.integrations()


@router.get("/analytics/recent", response_model=RecentActivityResponse, summary="Get recent task activity")
def analytics_recent(
    limit: int = 20,
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> RecentActivityResponse:
    """Return newest task activity with a bounded result limit."""
    return RecentActivityResponse(items=analytics.recent(limit))


def _to_business_task(request: TaskCreateRequest) -> BusinessTask:
    """Transform an API request into the existing domain model."""
    return BusinessTask(
        task_id=request.task_id or f"api-{uuid4().hex[:12]}",
        source=request.source,
        title=request.title,
        content=request.content,
        metadata=request.metadata,
    )


def _result_response(task: BusinessTask, result) -> TaskResponse:
    """Map the existing workflow result to the public API shape."""
    execution = result.execution_result
    return TaskResponse(
        task_id=task.task_id,
        source=task.source,
        analysis=result.analysis,
        planned_actions=result.planned_actions,
        execution_results=execution.actions if execution else [],
        integration_results=execution.integration_results if execution else [],
        final_status=result.status.value,
        processing_metadata=result.processing_metadata,
    )


@router.get("/health", response_model=HealthResponse, summary="Check service health")
def health(database: DatabaseManager = Depends(get_database_manager)) -> HealthResponse:
    """Return a lightweight health response without external dependencies."""
    database.count_tasks()
    return HealthResponse(status="healthy", service=_SERVICE_NAME)


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Process one business task",
    responses={400: {"description": "Task processing failed"}},
)
def create_task(
    request: TaskCreateRequest,
    workflow: Workflow = Depends(get_workflow),
) -> TaskResponse:
    """Process one task through the existing workflow."""
    task = _to_business_task(request)
    return _result_response(task, workflow.process(task))


@router.post(
    "/tasks/batch",
    response_model=BatchTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Process multiple business tasks sequentially",
)
def create_tasks_batch(
    requests: list[TaskCreateRequest],
    workflow: Workflow = Depends(get_workflow),
) -> BatchTaskResponse:
    """Process a deterministic batch without introducing background jobs."""
    results = []
    for request in requests:
        task = _to_business_task(request)
        try:
            results.append(_result_response(task, workflow.process(task)))
        except (DuplicateTaskError, WorkflowError) as error:
            results.append(
                TaskResponse(
                    task_id=task.task_id,
                    source=task.source,
                    final_status=WorkflowStatus.FAILED.value,
                    error="Task could not be processed.",
                    processing_metadata={
                        "failure_message": "Task processing failed.",
                        "lifecycle_status": "failed",
                    },
                )
            )
    return BatchTaskResponse(results=results)


@router.get(
    "/tasks/{task_id}",
    response_model=StoredTaskResponse,
    summary="Retrieve a stored task",
    responses={404: {"description": "Task was not found"}},
)
def get_task(
    task_id: str,
    database: DatabaseManager = Depends(get_database_manager),
) -> StoredTaskResponse:
    """Return task, analysis, and persisted action data when available."""
    record = database.get_task_record(task_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    task = record["task"]
    execution = record["execution_result"]
    failed = execution.failed_actions if execution else []
    return StoredTaskResponse(
        task_id=task.task_id,
        source=task.source,
        title=task.title,
        content=task.content,
        metadata=task.metadata,
        created_at=task.created_at,
        analysis=record["analysis"],
        planned_actions=record["planned_actions"],
        execution_results=execution.actions if execution else [],
        integration_results=execution.integration_results if execution else [],
        final_status=record["processing_metadata"].lifecycle_status.value,
        processing_metadata=record["processing_metadata"],
    )
