"""Shared interface and helpers for external task ingestion."""

from abc import ABC, abstractmethod
from typing import Any

from .models import BusinessTask


class TaskIngestion(ABC):
    """Convert one external input shape into a validated BusinessTask."""

    @abstractmethod
    def to_business_task(self, input_data: Any) -> BusinessTask:
        """Validate and transform an external input."""

    def ingest(self, input_data: Any) -> BusinessTask:
        """Convenient common entry point for single-input adapters."""
        return self.to_business_task(input_data)


def parse_model(model_type: type, value: Any) -> Any:
    """Support Pydantic v1 and v2 model parsing consistently."""
    if isinstance(value, model_type):
        return value
    if hasattr(model_type, "model_validate"):
        return model_type.model_validate(value)
    return model_type.parse_obj(value)