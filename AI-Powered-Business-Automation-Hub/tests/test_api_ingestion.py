import pytest

from src.api_ingestion import APIIngestion
from src.exceptions import InputValidationError


def test_valid_api_payload_transforms_to_business_task():
    payload = {
        "task_id": "api-001",
        "title": "Customer requests pricing information",
        "content": "Please send enterprise pricing details.",
        "source": "api",
        "metadata": {"customer_id": "customer-123"},
    }

    task = APIIngestion().to_business_task(payload)

    assert task.task_id == "api-001"
    assert task.source == "api"
    assert task.metadata == {"customer_id": "customer-123"}


def test_api_payload_defaults_source_to_api():
    task = APIIngestion().to_business_task(
        {"task_id": "api-002", "title": "A task", "content": "Details"}
    )

    assert task.source == "api"


def test_malformed_api_payload_is_rejected():
    with pytest.raises(InputValidationError, match="Invalid API input"):
        APIIngestion().to_business_task({"task_id": "api-003", "title": "Missing content"})


def test_blank_api_required_fields_are_rejected():
    with pytest.raises(InputValidationError, match="must not be empty"):
        APIIngestion().to_business_task(
            {"task_id": "api-004", "title": " ", "content": "Details", "source": "api"}
        )