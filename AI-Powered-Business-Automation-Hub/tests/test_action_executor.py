from src.action_executor import ActionExecutor
from src.models import ActionStatus, AutomationAction


def test_supported_actions_execute_successfully():
    actions = [
        AutomationAction(
            action_id="flag-1",
            action_type="flag_critical",
            description="Flag task",
        )
    ]

    result = ActionExecutor().execute("task-1", actions)

    assert result.task_id == "task-1"
    assert result.overall_status is ActionStatus.COMPLETED
    assert result.successful_actions == ["flag-1"]
    assert result.failed_actions == []
    assert result.actions[0].status is ActionStatus.COMPLETED
    assert result.actions[0].metadata["execution"] == "local_demo"


def test_unsupported_actions_are_captured_as_failures():
    action = AutomationAction(
        action_id="unknown-1",
        action_type="unknown_action",
        description="Unsupported action",
    )

    result = ActionExecutor().execute("task-2", [action])

    assert result.overall_status is ActionStatus.FAILED
    assert result.successful_actions == []
    assert result.failed_actions == ["unknown-1"]
    assert result.actions[0].status is ActionStatus.FAILED
    assert "Unsupported action type" in result.actions[0].metadata["error"]
