import pytest

from src.exceptions import UnsupportedIntegrationError
from src.integration_router import IntegrationRouter
from src.models import AutomationAction, BusinessTask, TaskAnalysis, TaskCategory, TaskPriority


def context(settings):
    task = BusinessTask(task_id="task-1", source="test", title="Support request", content="Help")
    analysis = TaskAnalysis(
        category=TaskCategory.SUPPORT,
        priority=TaskPriority.MEDIUM,
        summary="Support request.",
        confidence=0.9,
    )
    return task, analysis


def test_router_routes_notification_action(settings):
    task, analysis = context(settings)
    result = IntegrationRouter(settings).route(
        AutomationAction(
            action_id="notify-1",
            action_type="prepare_customer_response",
            description="Prepare response",
        ),
        task,
        analysis,
    )

    assert result.integration_name == "notification_connector"
    assert result.status.value == "simulated"


def test_router_routes_report_action(settings):
    task, analysis = context(settings)
    result = IntegrationRouter(settings).route(
        AutomationAction(
            action_id="report-1",
            action_type="create_incident_record",
            description="Create record",
        ),
        task,
        analysis,
    )

    assert result.integration_name == "report_connector"
    assert result.status.value == "completed"


def test_router_rejects_unknown_action(settings):
    task, _ = context(settings)

    with pytest.raises(UnsupportedIntegrationError, match="No integration connector supports"):
        IntegrationRouter(settings).route(
            AutomationAction(action_id="unknown", action_type="unknown", description="Unknown"),
            task,
        )