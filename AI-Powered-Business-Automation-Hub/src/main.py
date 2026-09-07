"""Runnable Phase 5 integration-layer demonstration."""

from datetime import datetime, timezone

from .api_ingestion import APIIngestion
from .analytics import AnalyticsService
from .csv_ingestion import CSVIngestion
from .config import Settings
from .database_manager import DatabaseManager
from .email_ingestion import EmailIngestion
from .input_models import EmailInput
from .logger import get_logger
from .workflow import Workflow


def main() -> None:
    """Run the local, credential-free demonstration workflow."""
    settings = Settings()
    logger = get_logger(log_directory=settings.logs_dir)
    database = DatabaseManager(settings)
    database.initialize()
    workflow = Workflow(database)
    email_task = EmailIngestion().to_business_task(
        EmailInput(
            message_id="phase7-email-001",
            sender="customer@example.com",
            subject="Customer cannot reset account password",
            body="Please help the customer regain access to their account.",
            received_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
    )
    csv_tasks = CSVIngestion().load_tasks(settings.data_input_dir / "sample_tasks.csv")
    api_task = APIIngestion().to_business_task(
        {
            "task_id": "phase7-api-001",
            "title": "Customer requests pricing information",
            "content": "Please send enterprise pricing details.",
            "source": "api",
            "metadata": {"customer_id": "customer-123"},
        }
    )
    tasks = [("Email", email_task), *(("CSV", task) for task in csv_tasks), ("API", api_task)]

    print("AI-Powered Business Automation Hub")
    print("==================================")
    print("System initialized successfully")
    print(f"Demo Mode: {settings.demo_mode}")
    print(f"Integration Simulation Mode: {settings.integration_simulation_mode}")
    print()
    for input_source, task in tasks:
        existing_record = database.get_task_record(task.task_id) if database.task_exists(task.task_id) else None
        result = workflow.process(task) if existing_record is None else None
        analysis = result.analysis if result else existing_record["analysis"]
        print(f"Input Source: {input_source}")
        print(f"Task: {task.task_id}")
        print(f"Category: {analysis.category.value}")
        print(f"Priority: {analysis.priority.value}")
        execution = result.execution_result if result else existing_record["execution_result"]
        print("Integrations:")
        for integration in execution.integration_results if execution else []:
            print(f"- {integration.integration_name}: {integration.status.value}")
        final_status = result.status.value if result else existing_record["processing_metadata"].lifecycle_status.value
        print(f"Final Status: {final_status}")
        print(f"Stored in database: {'Yes' if database.get_task(task.task_id) else 'No'}")
        print()
        logger.info("Demo task available: %s", task.task_id)

    overview = AnalyticsService(database).overview()
    print("Operational Summary")
    print(f"Total Tasks: {overview.total_tasks}")
    print(f"Completed Tasks: {overview.completed_tasks}")
    print(f"Failed Tasks: {overview.failed_tasks}")
    print(f"Completion Rate: {overview.completion_rate}%")
    print(f"Tasks by Category: {overview.tasks_by_category}")


if __name__ == "__main__":
    main()
