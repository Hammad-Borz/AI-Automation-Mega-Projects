"""Route integration-backed actions to independent connectors."""

import logging

from .config import Settings
from .exceptions import UnsupportedIntegrationError
from .integration_models import IntegrationRequest, IntegrationResult
from .models import AutomationAction, BusinessTask, TaskAnalysis
from .notification_connector import NotificationConnector
from .report_connector import ReportConnector
from .webhook_connector import WebhookConnector


class IntegrationRouter:
    """Select and invoke the connector associated with an action."""

    _NOTIFICATION_ACTIONS = {
        "prepare_customer_response",
        "prepare_operations_notification",
        "prepare_billing_response",
    }
    _REPORT_ACTIONS = {"create_incident_record", "create_sales_follow_up"}
    _WEBHOOK_ACTIONS = {"send_webhook", "trigger_webhook"}

    def __init__(self, settings: Settings | None = None, logger: logging.Logger | None = None) -> None:
        self.settings = settings or Settings()
        self.logger = logger or logging.getLogger("automation_hub")
        self.notification_connector = NotificationConnector(self.settings, self.logger)
        self.webhook_connector = WebhookConnector(self.settings, self.logger)
        self.report_connector = ReportConnector(self.settings, self.logger)

    def route(
        self,
        action: AutomationAction,
        task: BusinessTask,
        analysis: TaskAnalysis | None = None,
    ) -> IntegrationResult:
        """Route an action or raise clearly for unsupported integration actions."""
        request_payload = {"message": action.description, **action.metadata}
        if action.action_type in self._WEBHOOK_ACTIONS:
            request_payload = {
                "event": action.action_type,
                "data": {"task_id": task.task_id, **action.metadata},
            }
        request = IntegrationRequest(
            integration_name=self.integration_name_for(action.action_type),
            action_name=action.action_type,
            task_id=task.task_id,
            payload=request_payload,
            metadata={
                "category": analysis.category.value if analysis else None,
                "priority": analysis.priority.value if analysis else None,
                "execution_status": action.status.value,
            },
        )
        if action.action_type in self._NOTIFICATION_ACTIONS:
            return self.notification_connector.execute(request, analysis)
        if action.action_type in self._REPORT_ACTIONS:
            return self.report_connector.execute(request, analysis)
        if action.action_type in self._WEBHOOK_ACTIONS:
            return self.webhook_connector.execute(request)
        raise UnsupportedIntegrationError(f"No integration connector supports '{action.action_type}'.")

    def supports(self, action_type: str) -> bool:
        """Return whether an action has an integration connector."""
        return action_type in self._NOTIFICATION_ACTIONS | self._REPORT_ACTIONS | self._WEBHOOK_ACTIONS

    def integration_name_for(self, action_type: str) -> str:
        """Return the connector name for a supported action."""
        if action_type in self._NOTIFICATION_ACTIONS:
            return "notification_connector"
        if action_type in self._REPORT_ACTIONS:
            return "report_connector"
        if action_type in self._WEBHOOK_ACTIONS:
            return "webhook_connector"
        raise UnsupportedIntegrationError(f"No integration connector supports '{action_type}'.")