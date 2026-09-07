"""Local notification integration simulation."""

import logging

from .config import Settings
from .integration_models import IntegrationRequest, IntegrationResult, IntegrationStatus
from .models import TaskAnalysis


class NotificationConnector:
    """Generate and simulate notification delivery without sending messages."""

    def __init__(self, settings: Settings | None = None, logger: logging.Logger | None = None) -> None:
        self.settings = settings or Settings()
        self.logger = logger or logging.getLogger("automation_hub")

    def execute(self, request: IntegrationRequest, analysis: TaskAnalysis | None = None) -> IntegrationResult:
        """Create a deterministic notification payload and simulate delivery."""
        recipient = self._recipient_group(request.action_name)
        priority = analysis.priority.value if analysis else request.metadata.get("priority", "unknown")
        payload = {
            "recipient_group": recipient,
            "subject": f"Automation task {request.task_id}",
            "message": request.payload.get("message", request.action_name),
            "task_id": request.task_id,
            "priority": priority,
        }
        status = IntegrationStatus.SIMULATED if self.settings.integration_simulation_mode else IntegrationStatus.SKIPPED
        self.logger.info("Notification integration %s: %s", status.value, request.action_name)
        return IntegrationResult(
            integration_name="notification_connector",
            action_name=request.action_name,
            task_id=request.task_id,
            status=status,
            message="Notification delivery simulated locally."
            if status is IntegrationStatus.SIMULATED
            else "Notification delivery skipped because simulation mode is disabled.",
            payload=payload,
        )

    @staticmethod
    def _recipient_group(action_name: str) -> str:
        if "operations" in action_name or "incident" in action_name:
            return "operations_team"
        if "customer" in action_name or "support" in action_name:
            return "support_queue"
        if "sales" in action_name:
            return "sales_team"
        if "billing" in action_name:
            return "billing_team"
        return "business_automation_team"