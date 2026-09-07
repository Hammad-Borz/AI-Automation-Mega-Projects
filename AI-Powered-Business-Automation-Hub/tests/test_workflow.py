import pytest

from src.exceptions import DuplicateTaskError, WorkflowError
from src.models import BusinessTask, TaskLifecycle, WorkflowStatus
from src.ai_analyzer import AIAnalyzer
from src.workflow import Workflow


def test_workflow_validates_and_stores_task(database):
    task = BusinessTask(
        task_id="task-1",
        source="manual",
        title="Run workflow",
        content="Store this task.",
    )

    result = Workflow(database).process(task)

    assert result.task_id == "task-1"
    assert result.status is WorkflowStatus.COMPLETED
    assert result.actions == ["validated", "stored"]
    assert result.analysis is not None
    assert result.analysis.category.value == "general"
    assert database.get_analysis(task.task_id) == result.analysis
    assert result.planned_actions[0].action_type == "mark_for_general_review"
    assert result.execution_result is not None
    assert result.execution_result.overall_status.value == "completed"
    assert database.get_actions(task.task_id) == result.execution_result.actions
    assert database.count_tasks() == 1


def test_workflow_wraps_invalid_input(database):
    invalid_task = BusinessTask(
        task_id="task-2",
        source="manual",
        title="   ",
        content="Content",
    )

    with pytest.raises(WorkflowError, match="Task title must not be empty"):
        Workflow(database).process(invalid_task)

    assert database.count_tasks() == 0


def test_workflow_returns_and_persists_integration_results(database):
    task = BusinessTask(
        task_id="task-critical",
        source="monitoring",
        title="Production checkout outage",
        content="The checkout service is unavailable and requires an emergency response.",
    )

    result = Workflow(database).process(task)

    assert result.execution_result is not None
    assert [item.integration_name for item in result.execution_result.integration_results] == [
        "report_connector",
        "notification_connector",
    ]
    assert all(item.status.value in {"completed", "simulated"} for item in result.execution_result.integration_results)


def test_successful_workflow_persists_completed_lifecycle(database):
    task = BusinessTask(task_id="lifecycle-1", source="test", title="Lifecycle", content="Complete this task.")

    Workflow(database).process(task)

    record = database.get_task_record(task.task_id)
    assert record["processing_metadata"].lifecycle_status is TaskLifecycle.COMPLETED
    assert record["processing_metadata"].processing_completed_at is not None
    assert record["processing_metadata"].processing_duration_ms >= 0
    assert record["planned_actions"]
    assert record["execution_result"] is not None


def test_duplicate_task_ids_are_rejected(database):
    task = BusinessTask(task_id="duplicate-1", source="test", title="Duplicate", content="Original task.")
    workflow = Workflow(database)

    workflow.process(task)
    with pytest.raises(DuplicateTaskError, match="already exists"):
        workflow.process(task)

    assert database.count_tasks() == 1


class FailingAnalyzer:
    def analyze(self, task):
        raise RuntimeError("private provider detail")


def test_processing_failure_is_persisted_without_leaking_details(database):
    task = BusinessTask(task_id="failure-1", source="test", title="Failure", content="Trigger failure.")

    with pytest.raises(WorkflowError, match="Could not process task") as error:
        Workflow(database, analyzer=FailingAnalyzer()).process(task)

    record = database.get_task_record(task.task_id)
    assert record["processing_metadata"].lifecycle_status is TaskLifecycle.FAILED
    assert record["processing_metadata"].failure_message == "Task processing failed."
    assert "private provider detail" in str(error.value)
