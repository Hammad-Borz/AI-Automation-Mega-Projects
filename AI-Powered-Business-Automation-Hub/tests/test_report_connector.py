import json

from src.integration_models import IntegrationRequest
from src.report_connector import ReportConnector


def test_report_connector_creates_local_event_record(settings):
    result = ReportConnector(settings).execute(
        IntegrationRequest(
            integration_name="report_connector",
            action_name="create_incident_record",
            task_id="task-1",
            metadata={"category": "urgent", "priority": "critical"},
        )
    )

    output_path = settings.output_directory / "task-1_create_incident_record.json"
    assert result.status.value == "completed"
    assert output_path.exists()
    event = json.loads(output_path.read_text(encoding="utf-8"))
    assert event["task_id"] == "task-1"
    assert event["category"] == "urgent"
    assert event["priority"] == "critical"