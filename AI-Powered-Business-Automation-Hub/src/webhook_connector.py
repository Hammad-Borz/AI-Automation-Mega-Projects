"""Safe webhook integration boundary with local simulation."""

import logging
from typing import Any

from .config import Settings
from .exceptions import ConnectorExecutionError
from .integration_models import IntegrationRequest, IntegrationResult, IntegrationStatus


class WebhookConnector:
    """Validate webhook payloads and simulate delivery without network access."""

    def __init__(self, settings: Settings | None = None, logger: logging.Logger | None = None) -> None:
        self.settings = settings or Settings()
        self.logger = logger or logging.getLogger("automation_hub")

    def execute(self, request: IntegrationRequest) -> IntegrationResult:
        """Return a local result for a valid webhook request."""
        self._validate_payload(request.payload)
        status = IntegrationStatus.SIMULATED if self.settings.integration_simulation_mode else IntegrationStatus.SKIPPED
        self.logger.info("Webhook integration %s: %s", status.value, request.action_name)
        return IntegrationResult(
            integration_name="webhook_connector",
            action_name=request.action_name,
            task_id=request.task_id,
            status=status,
            message="Webhook delivery simulated locally."
            if status is IntegrationStatus.SIMULATED
            else "Webhook delivery skipped because it is disabled.",
            payload=request.payload,
        )

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict) or not payload:
            raise ConnectorExecutionError("Webhook payload must be a non-empty dictionary.")
        if not payload.get("event") or not payload.get("data"):
            raise ConnectorExecutionError("Webhook payload requires 'event' and 'data'.")