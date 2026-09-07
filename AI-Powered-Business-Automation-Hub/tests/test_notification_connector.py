from src.integration_models import IntegrationRequest
from src.notification_connector import NotificationConnector


def test_notification_connector_builds_simulated_payload(settings):
    result = NotificationConnector(settings).execute(
        IntegrationRequest(
            integration_name="notification_connector",
            action_name="prepare_operations_notification",
            task_id="task-1",
            payload={"message": "Incident requires attention"},
            metadata={"priority": "critical"},
        )
    )

    assert result.status.value == "simulated"
    assert result.payload["recipient_group"] == "operations_team"
    assert result.payload["priority"] == "critical"
    assert result.payload["task_id"] == "task-1"