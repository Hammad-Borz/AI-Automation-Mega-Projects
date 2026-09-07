"""Validation rules for business tasks."""

from .exceptions import ValidationError
from .models import BusinessTask


def validate_business_task(task: BusinessTask) -> BusinessTask:
    """Validate required task fields and return the unchanged task."""
    if not task.task_id or not task.task_id.strip():
        raise ValidationError("Task ID is required.")
    if not task.source or not task.source.strip():
        raise ValidationError("Task source is required.")
    if not task.title or not task.title.strip():
        raise ValidationError("Task title must not be empty.")
    if not task.content or not task.content.strip():
        raise ValidationError("Task content must not be empty.")
    return task
