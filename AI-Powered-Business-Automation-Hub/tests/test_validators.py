import pytest

from src.exceptions import ValidationError
from src.models import BusinessTask
from src.validators import validate_business_task


def make_task(**changes):
    values = {
        "task_id": "task-1",
        "source": "manual",
        "title": "A valid title",
        "content": "Valid content",
    }
    values.update(changes)
    return BusinessTask(**values)


def test_validator_accepts_valid_task():
    task = make_task()

    assert validate_business_task(task) is task


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("task_id", "Task ID is required."),
        ("source", "Task source is required."),
        ("title", "Task title must not be empty."),
        ("content", "Task content must not be empty."),
    ],
)
def test_validator_rejects_blank_required_fields(field, message):
    with pytest.raises(ValidationError, match=message):
        validate_business_task(make_task(**{field: "  "}))
