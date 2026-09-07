"""Deterministic business automation planning rules."""

from .models import (
    AutomationAction,
    TaskAnalysis,
    TaskCategory,
    TaskPriority,
)


class AutomationRulesEngine:
    """Translate task analysis into actions without executing them."""

    def plan_actions(self, analysis: TaskAnalysis) -> list[AutomationAction]:
        """Return deterministic actions for the supplied analysis."""
        actions: list[AutomationAction] = []
        if analysis.category is TaskCategory.URGENT and analysis.priority is TaskPriority.CRITICAL:
            actions.extend(
                [
                    self._action("flag_critical", "Flag task as critical"),
                    self._action("create_incident_record", "Create a local incident record"),
                    self._action(
                        "prepare_operations_notification",
                        "Prepare an operations notification payload",
                    ),
                ]
            )
        elif analysis.category is TaskCategory.SUPPORT:
            actions.extend(
                [
                    self._action("assign_support_queue", "Assign task to the support queue"),
                    self._action("prepare_customer_response", "Prepare a customer response payload"),
                ]
            )
        elif analysis.category is TaskCategory.SALES:
            actions.extend(
                [
                    self._action("assign_sales_team", "Assign task to the sales team"),
                    self._action("create_sales_follow_up", "Create a local sales follow-up"),
                ]
            )
        elif analysis.category is TaskCategory.BILLING:
            actions.extend(
                [
                    self._action("assign_billing_review", "Assign task for billing review"),
                    self._action("prepare_billing_response", "Prepare a billing response payload"),
                ]
            )
        elif analysis.category is TaskCategory.OPERATIONS:
            actions.extend(
                [
                    self._action("assign_operations_team", "Assign task to the operations team"),
                    self._action("prepare_operations_review", "Prepare an operations review"),
                ]
            )
        else:
            actions.append(self._action("mark_for_general_review", "Mark task for general review"))
        return actions

    @staticmethod
    def _action(action_type: str, description: str) -> AutomationAction:
        return AutomationAction(
            action_id=action_type,
            action_type=action_type,
            description=description,
        )