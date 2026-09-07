import pytest

from src.exceptions import ConnectorExecutionError
from src.integration_models import IntegrationRequest
from src.webhook_connector import WebhookConnector


def test_webhook_connector_simulates_delivery(settings):
    result = WebhookConnector(settings).execute(
        IntegrationRequest(
            integration_name="webhook_connector",
            action_name="send_webhook",
            task_id="task-1",
            payload={"event": "task.completed", "data": {"task_id": "task-1"}},
        )
    )

    assert result.status.value == "simulated"
    assert result.payload["event"] == "task.completed"


def test_webhook_connector_rejects_malformed_payload(settings):
    with pytest.raises(ConnectorExecutionError, match="requires 'event' and 'data'"):
        WebhookConnector(settings).execute(
            IntegrationRequest(
                integration_name="webhook_connector",
                action_name="send_webhook",
                task_id="task-1",
                payload={"event": "task.completed"},
            )
        )