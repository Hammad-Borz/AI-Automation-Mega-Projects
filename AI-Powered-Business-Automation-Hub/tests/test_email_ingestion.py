from datetime import datetime, timezone

import pytest

from src.email_ingestion import EmailIngestion
from src.exceptions import InputValidationError
from src.input_models import EmailInput


def test_valid_email_transforms_to_business_task():
    email = EmailInput(
        message_id="message-001",
        sender="customer@example.com",
        subject="Cannot access account",
        body="Please help me sign in.",
        received_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        metadata={"thread": "thread-1"},
    )

    task = EmailIngestion().to_business_task(email)

    assert task.task_id == "message-001"
    assert task.source == "email"
    assert task.title == "Cannot access account"
    assert task.metadata["sender"] == "customer@example.com"
    assert task.metadata["thread"] == "thread-1"


def test_email_without_message_id_gets_deterministic_id():
    data = {
        "sender": "customer@example.com",
        "subject": "Question",
        "body": "Need help.",
        "received_at": "2026-01-01T00:00:00+00:00",
    }

    first = EmailIngestion().to_business_task(data)
    second = EmailIngestion().to_business_task(data)

    assert first.task_id.startswith("email-")
    assert first.task_id == second.task_id


def test_invalid_email_is_rejected():
    with pytest.raises(InputValidationError, match="Invalid email input"):
        EmailIngestion().to_business_task({"sender": "", "subject": "Subject", "body": "Body"})