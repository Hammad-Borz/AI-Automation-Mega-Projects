"""Local structured email ingestion."""

import hashlib
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from .exceptions import InputValidationError
from .input_models import EmailInput
from .models import BusinessTask
from .task_ingestion import TaskIngestion, parse_model


class EmailIngestion(TaskIngestion):
    """Transform validated local email data into a BusinessTask."""

    def to_business_task(self, input_data: EmailInput | dict[str, Any]) -> BusinessTask:
        try:
            email = parse_model(EmailInput, input_data)
            if not email.sender.strip() or not email.subject.strip() or not email.body.strip():
                raise ValueError("sender, subject, and body must not be empty")
            task_id = email.message_id.strip() if email.message_id and email.message_id.strip() else self._task_id(email)
            metadata = {
                **email.metadata,
                "sender": email.sender,
                "message_id": email.message_id,
                "received_at": email.received_at.isoformat(),
            }
            return BusinessTask(
                task_id=task_id,
                source="email",
                title=email.subject.strip(),
                content=email.body.strip(),
                metadata=metadata,
                created_at=email.received_at,
            )
        except (PydanticValidationError, ValueError, TypeError) as error:
            raise InputValidationError(f"Invalid email input: {error}") from error

    @staticmethod
    def _task_id(email: EmailInput) -> str:
        digest = hashlib.sha256(
            f"{email.sender}\n{email.subject}\n{email.received_at.isoformat()}".encode()
        ).hexdigest()[:12]
        return f"email-{digest}"