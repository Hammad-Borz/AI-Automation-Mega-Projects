from datetime import datetime, timezone

from src.models import AutomationResult, BusinessTask, WorkflowStatus


def test_business_task_uses_sensible_defaults():
    task = BusinessTask(task_id="task-1", source="email", title="A title", content="Details")

    assert task.metadata == {}
    assert isinstance(task.created_at, datetime)
    assert task.created_at.tzinfo == timezone.utc


def test_automation_result_defaults_actions():
    result = AutomationResult(
        task_id="task-1",
        status=WorkflowStatus.COMPLETED,
        message="Stored",
    )

    assert result.actions == []
    assert result.status.value == "completed"
