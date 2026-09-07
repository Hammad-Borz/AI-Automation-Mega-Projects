from datetime import datetime, timezone

from src.analytics import AnalyticsService
from src.models import BusinessTask, ProcessingMetadata, TaskLifecycle, TaskAnalysis, TaskCategory, TaskPriority
from src.workflow import Workflow


def test_empty_database_analytics_are_safe(database):
    service = AnalyticsService(database)

    overview = service.overview()
    performance = service.performance()
    integrations = service.integrations()
    recent = service.recent()

    assert overview.total_tasks == 0
    assert overview.completion_rate == 0.0
    assert overview.failure_rate == 0.0
    assert performance.tasks_with_duration == 0
    assert performance.average_duration is None
    assert integrations.total_events == 0
    assert recent == []


def save_task(database, task_id, source, category, priority):
    task = BusinessTask(task_id=task_id, source=source, title=task_id, content="Content")
    database.save_task(task)
    database.save_analysis(
        task_id,
        TaskAnalysis(
            category=category,
            priority=priority,
            summary=f"{task_id}.",
            confidence=0.9,
        ),
    )
    return task


def test_overview_aggregates_status_sources_categories_and_priorities(database):
    first = save_task(database, "task-a", "email", TaskCategory.SUPPORT, TaskPriority.MEDIUM)
    second = save_task(database, "task-b", "api", TaskCategory.SALES, TaskPriority.HIGH)
    database.save_processing(first.task_id, ProcessingMetadata(lifecycle_status=TaskLifecycle.COMPLETED))
    database.save_processing(second.task_id, ProcessingMetadata(lifecycle_status=TaskLifecycle.FAILED))

    overview = AnalyticsService(database).overview()

    assert overview.total_tasks == 2
    assert overview.completed_tasks == 1
    assert overview.failed_tasks == 1
    assert overview.completion_rate == 50.0
    assert overview.failure_rate == 50.0
    assert overview.tasks_by_source == {"email": 1, "api": 1}
    assert overview.tasks_by_category == {"support": 1, "sales": 1}
    assert overview.tasks_by_priority == {"medium": 1, "high": 1}


def test_performance_uses_only_available_duration_data(database):
    task = save_task(database, "timed", "api", TaskCategory.GENERAL, TaskPriority.LOW)
    database.save_processing(
        task.task_id,
        ProcessingMetadata(
            lifecycle_status=TaskLifecycle.COMPLETED,
            processing_started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            processing_completed_at=datetime(2026, 1, 1, 0, 0, 2, tzinfo=timezone.utc),
            processing_duration_ms=2000,
        ),
    )

    performance = AnalyticsService(database).performance()

    assert performance.tasks_with_duration == 1
    assert performance.average_duration == 2.0
    assert performance.minimum_duration == 2.0
    assert performance.maximum_duration == 2.0


def test_recent_activity_is_newest_first_and_bounded(database):
    save_task(database, "old", "api", TaskCategory.GENERAL, TaskPriority.LOW)
    save_task(database, "new", "email", TaskCategory.SUPPORT, TaskPriority.MEDIUM)

    recent = AnalyticsService(database).recent(limit=1)

    assert len(recent) == 1
    assert recent[0].task_id == "new"
    assert recent[0].status == "received"


def test_recent_limit_is_safely_capped(database):
    save_task(database, "one", "api", TaskCategory.GENERAL, TaskPriority.LOW)

    assert len(AnalyticsService(database).recent(limit=10000)) == 1
    assert len(AnalyticsService(database).recent(limit=0)) == 1


def test_integration_analytics_uses_persisted_results(database):
    Workflow(database).process(
        BusinessTask(
            task_id="integration-analytics",
            source="email",
            title="Customer cannot reset password",
            content="Support needs to help the customer.",
        )
    )

    integrations = AnalyticsService(database).integrations()

    assert integrations.total_events == 1
    assert integrations.by_integration == {"notification_connector": 1}
    assert integrations.by_status == {"simulated": 1}
