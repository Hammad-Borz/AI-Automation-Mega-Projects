"""Safe local execution of planned automation actions."""

import logging

from .models import ActionStatus, AutomationAction, AutomationExecutionResult
from .models import BusinessTask, TaskAnalysis
from .integration_models import IntegrationResult
from .integration_router import IntegrationRouter


class ActionExecutor:
    """Execute supported actions locally without external side effects."""

    _SUPPORTED_ACTIONS = {
        "flag_critical",
        "create_incident_record",
        "prepare_operations_notification",
        "assign_support_queue",
        "prepare_customer_response",
        "assign_sales_team",
        "create_sales_follow_up",
        "assign_billing_review",
        "prepare_billing_response",
        "assign_operations_team",
        "prepare_operations_review",
        "mark_for_general_review",
        "send_webhook",
        "trigger_webhook",
    }

    def __init__(
        self,
        logger: logging.Logger | None = None,
        integration_router: IntegrationRouter | None = None,
    ) -> None:
        self.logger = logger or logging.getLogger("automation_hub")
        self.integration_router = integration_router

    def execute(
        self,
        task_id: str,
        actions: list[AutomationAction],
        task: BusinessTask | None = None,
        analysis: TaskAnalysis | None = None,
    ) -> AutomationExecutionResult:
        """Execute each action and capture failures without hiding them."""
        executed_actions: list[AutomationAction] = []
        successful_actions: list[str] = []
        failed_actions: list[str] = []
        integration_results: list[IntegrationResult] = []
        for action in actions:
            self.logger.info("Action execution started: %s", action.action_id)
            try:
                if action.action_type not in self._SUPPORTED_ACTIONS:
                    raise ValueError(f"Unsupported action type: {action.action_type}")
                integration_result = None
                if self.integration_router and self.integration_router.supports(action.action_type):
                    if task is None:
                        raise ValueError("Task context is required for integration-backed actions")
                    integration_result = self.integration_router.route(action, task, analysis)
                    integration_results.append(integration_result)
                executed = self._updated_action(
                    action,
                    ActionStatus.COMPLETED,
                    {
                        **action.metadata,
                        "execution": "local_demo",
                        **({"integration_status": integration_result.status.value} if integration_result else {}),
                    },
                )
                successful_actions.append(action.action_id)
                self.logger.info("Action execution completed: %s", action.action_id)
            except Exception as error:
                executed = self._updated_action(
                    action,
                    ActionStatus.FAILED,
                    {**action.metadata, "error": str(error)},
                )
                failed_actions.append(action.action_id)
                self.logger.error("Action execution failed: %s (%s)", action.action_id, error)
            executed_actions.append(executed)

        overall_status = ActionStatus.FAILED if failed_actions else ActionStatus.COMPLETED
        return AutomationExecutionResult(
            task_id=task_id,
            actions=executed_actions,
            successful_actions=successful_actions,
            failed_actions=failed_actions,
            overall_status=overall_status,
            integration_results=integration_results,
        )

    @staticmethod
    def _updated_action(
        action: AutomationAction, status: ActionStatus, metadata: dict[str, str]
    ) -> AutomationAction:
        """Copy an action across supported Pydantic major versions."""
        if hasattr(action, "model_copy"):
            return action.model_copy(update={"status": status, "metadata": metadata})
        return action.copy(update={"status": status, "metadata": metadata})