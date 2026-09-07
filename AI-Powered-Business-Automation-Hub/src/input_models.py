"""Validated models for external task input formats."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class EmailInput(BaseModel):
    """Structured email data before conversion to a business task."""

    message_id: str | None = None
    sender: str
    subject: str
    body: str
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class CSVTaskRow(BaseModel):
    """A validated row from the supported task CSV format."""

    task_id: str
    title: str
    content: str
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class APIInput(BaseModel):
    """A validated dictionary payload from a future API boundary."""

    task_id: str
    title: str
    content: str
    source: str = "api"
    metadata: dict[str, Any] = Field(default_factory=dict)