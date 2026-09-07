"""Local automation event report generation."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings
from .integration_models import IntegrationRequest, IntegrationResult, IntegrationStatus
from .models import TaskAnalysis


class ReportConnector:
    """Write structured local event records for executed actions."""

    def __init__(self, settings: Settings | None = None, logger: logging.Logger | None = None) -> None:
        self.settings = settings or Settings()
        self.logger = logger or logging.getLogger("automation_hub")

    def execute(self, request: IntegrationRequest, analysis: TaskAnalysis | None = None) -> IntegrationResult:
        """Create a JSON event record in the configured output directory."""
        timestamp = datetime.now(timezone.utc)
        event = {
            "task_id": request.task_id,
            "action": request.action_name,
            "category": analysis.category.value if analysis else request.metadata.get("category"),
            "priority": analysis.priority.value if analysis else request.metadata.get("priority"),
            "execution_status": request.metadata.get("execution_status", "completed"),
            "timestamp": timestamp.isoformat(),
        }
        output_path = Path(self.settings.output_directory) / f"{request.task_id}_{request.action_name}.json"
        output_path.write_text(json.dumps(event, indent=2), encoding="utf-8")
        self.logger.info("Report event created: %s", output_path.name)
        return IntegrationResult(
            integration_name="report_connector",
            action_name=request.action_name,
            task_id=request.task_id,
            status=IntegrationStatus.COMPLETED,
            message="Local automation event record created.",
            payload=event,
            metadata={"output_path": str(output_path)},
            executed_at=timestamp,
        )