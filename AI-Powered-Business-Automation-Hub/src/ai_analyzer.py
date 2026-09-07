"""Deterministic task analysis with a future provider integration boundary."""

from .config import Settings
from .exceptions import WorkflowError
from .models import BusinessTask, TaskAnalysis, TaskCategory, TaskPriority


class AIAnalyzer:
    """Analyze business tasks using demo rules or a future LLM provider."""

    def __init__(self, settings: Settings | None = None, demo_mode: bool | None = None) -> None:
        self.settings = settings or Settings()
        self.demo_mode = self.settings.demo_mode if demo_mode is None else demo_mode

    def analyze(self, task: BusinessTask) -> TaskAnalysis:
        """Return structured analysis without making external calls in demo mode."""
        if not self.demo_mode:
            raise WorkflowError(
                f"AI provider '{self.settings.ai_provider}' is not implemented; enable demo mode."
            )
        return self._analyze_demo(task)

    def _analyze_demo(self, task: BusinessTask) -> TaskAnalysis:
        text = f"{task.title} {task.content}".lower()
        category = self._classify_category(text)
        priority = self._classify_priority(text)
        return TaskAnalysis(
            category=category,
            priority=priority,
            summary=self._summary(task.title),
            confidence=self._confidence(category, priority),
            recommended_actions=self._recommended_actions(category, priority),
        )

    @staticmethod
    def _classify_category(text: str) -> TaskCategory:
        if any(keyword in text for keyword in ("outage", "unavailable", "production down", "critical incident")):
            return TaskCategory.URGENT
        if any(keyword in text for keyword in ("support", "login", "password", "cannot access", "error")):
            return TaskCategory.SUPPORT
        if any(keyword in text for keyword in ("sales", "quote", "pricing", "prospect", "purchase", "demo request")):
            return TaskCategory.SALES
        if any(keyword in text for keyword in ("billing", "invoice", "payment", "charge", "refund")):
            return TaskCategory.BILLING
        if any(keyword in text for keyword in ("urgent", "asap", "immediately", "emergency")):
            return TaskCategory.URGENT
        if any(keyword in text for keyword in ("operations", "operational", "inventory", "shipment", "deployment")):
            return TaskCategory.OPERATIONS
        return TaskCategory.GENERAL

    @staticmethod
    def _classify_priority(text: str) -> TaskPriority:
        if any(keyword in text for keyword in ("critical", "outage", "unavailable", "production down", "emergency")):
            return TaskPriority.CRITICAL
        if any(keyword in text for keyword in ("urgent", "asap", "immediately", "high priority", "incident")):
            return TaskPriority.HIGH
        if any(
            keyword in text
            for keyword in (
                "billing",
                "invoice",
                "payment",
                "support",
                "password",
                "cannot access",
                "reset",
                "sales",
                "quote",
                "pricing",
                "prospect",
                "purchase",
                "demo",
            )
        ):
            return TaskPriority.MEDIUM
        return TaskPriority.LOW

    @staticmethod
    def _summary(title: str) -> str:
        summary = title.strip()
        if not summary.endswith((".", "!", "?")):
            summary += "."
        return summary[:160]

    @staticmethod
    def _confidence(category: TaskCategory, priority: TaskPriority) -> float:
        if category is TaskCategory.GENERAL:
            return 0.60
        if priority is TaskPriority.CRITICAL:
            return 0.98
        return 0.92

    @staticmethod
    def _recommended_actions(category: TaskCategory, priority: TaskPriority) -> list[str]:
        actions: list[str] = []
        if priority is TaskPriority.CRITICAL:
            actions.append("Flag as critical")
        elif priority is TaskPriority.HIGH:
            actions.append("Prioritize for immediate review")
        if category is TaskCategory.URGENT:
            actions.extend(["Notify operations team", "Create incident record"])
        elif category is TaskCategory.SUPPORT:
            actions.extend(["Assign to support queue", "Respond to customer"])
        elif category is TaskCategory.SALES:
            actions.extend(["Assign to sales team", "Prepare follow-up"])
        elif category is TaskCategory.BILLING:
            actions.extend(["Review account records", "Assign to billing team"])
        elif category is TaskCategory.OPERATIONS:
            actions.append("Assign to operations team")
        else:
            actions.append("Review and route task")
        return actions