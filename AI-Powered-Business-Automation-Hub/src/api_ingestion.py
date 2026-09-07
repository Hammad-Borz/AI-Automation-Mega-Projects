"""JSON/API-style dictionary ingestion boundary."""

from typing import Any

from pydantic import ValidationError as PydanticValidationError

from .exceptions import InputValidationError
from .input_models import APIInput
from .models import BusinessTask
from .task_ingestion import TaskIngestion, parse_model


class APIIngestion(TaskIngestion):
    """Validate future API payloads and convert them into BusinessTask objects."""

    def to_business_task(self, input_data: dict[str, Any]) -> BusinessTask:
        try:
            payload = parse_model(APIInput, input_data)
            if (
                not payload.task_id.strip()
                or not payload.title.strip()
                or not payload.content.strip()
                or not payload.source.strip()
            ):
                raise ValueError("task_id, title, content, and source must not be empty")
            return BusinessTask(
                task_id=payload.task_id.strip(),
                source=payload.source.strip(),
                title=payload.title.strip(),
                content=payload.content.strip(),
                metadata=payload.metadata,
            )
        except (PydanticValidationError, ValueError, TypeError) as error:
            raise InputValidationError(f"Invalid API input: {error}") from error