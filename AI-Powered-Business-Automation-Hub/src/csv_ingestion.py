"""CSV task-file ingestion."""

import csv
from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from .exceptions import InputValidationError, UnsupportedInputError
from .input_models import CSVTaskRow
from .models import BusinessTask
from .task_ingestion import parse_model


class CSVIngestion:
    """Load supported CSV rows and convert them into BusinessTask objects."""

    REQUIRED_COLUMNS = {"task_id", "title", "content", "source"}

    def load_tasks(self, file_path: str | Path) -> list[BusinessTask]:
        """Read and validate every row from a CSV task file."""
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise InputValidationError(f"CSV file does not exist: {path}")
        if path.suffix.lower() != ".csv":
            raise UnsupportedInputError(f"Unsupported input file type: {path.suffix or '<none>'}")

        try:
            with path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                columns = set(reader.fieldnames or [])
                missing = self.REQUIRED_COLUMNS - columns
                if missing:
                    names = ", ".join(sorted(missing))
                    raise InputValidationError(f"CSV is missing required columns: {names}")
                tasks = []
                for row_number, row in enumerate(reader, start=2):
                    try:
                        parsed = parse_model(CSVTaskRow, self._normalize_row(row))
                        values = (parsed.task_id, parsed.title, parsed.content, parsed.source)
                        if any(not value.strip() for value in values):
                            raise ValueError("task_id, title, content, and source must not be empty")
                        tasks.append(
                            BusinessTask(
                                task_id=parsed.task_id.strip(),
                                source=parsed.source.strip(),
                                title=parsed.title.strip(),
                                content=parsed.content.strip(),
                                metadata=parsed.metadata,
                            )
                        )
                    except (PydanticValidationError, ValueError, TypeError) as error:
                        raise InputValidationError(f"Invalid CSV row {row_number}: {error}") from error
                return tasks
        except UnicodeDecodeError as error:
            raise InputValidationError(f"CSV file is not valid UTF-8: {path}") from error

    def ingest(self, file_path: str | Path) -> list[BusinessTask]:
        """Common ingestion entry point for a CSV file."""
        return self.load_tasks(file_path)

    @staticmethod
    def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
        metadata = row.get("metadata", "")
        return {**row, "metadata": {} if not metadata else {"value": metadata}}