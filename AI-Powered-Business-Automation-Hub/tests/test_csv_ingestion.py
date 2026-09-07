from pathlib import Path

import pytest

from src.csv_ingestion import CSVIngestion
from src.exceptions import InputValidationError, UnsupportedInputError


def write_csv(tmp_path: Path, content: str, name: str = "tasks.csv") -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_valid_csv_loads_tasks(tmp_path):
    path = write_csv(
        tmp_path,
        "task_id,title,content,source,metadata\n"
        "csv-001,Request pricing,Send a quote.,csv,priority=medium\n",
    )

    tasks = CSVIngestion().load_tasks(path)

    assert len(tasks) == 1
    assert tasks[0].task_id == "csv-001"
    assert tasks[0].source == "csv"
    assert tasks[0].metadata == {"value": "priority=medium"}


def test_missing_csv_is_rejected(tmp_path):
    with pytest.raises(InputValidationError, match="does not exist"):
        CSVIngestion().load_tasks(tmp_path / "missing.csv")


def test_unsupported_file_is_rejected(tmp_path):
    path = write_csv(tmp_path, "task_id,title,content,source\n1,T,C,S\n", "tasks.txt")

    with pytest.raises(UnsupportedInputError, match="Unsupported input file type"):
        CSVIngestion().load_tasks(path)


def test_missing_required_columns_are_rejected(tmp_path):
    path = write_csv(tmp_path, "task_id,title\n1,Title\n")

    with pytest.raises(InputValidationError, match="missing required columns"):
        CSVIngestion().load_tasks(path)


def test_malformed_rows_are_rejected(tmp_path):
    path = write_csv(tmp_path, "task_id,title,content,source\n,Title,Content,csv\n")

    with pytest.raises(InputValidationError, match="Invalid CSV row"):
        CSVIngestion().load_tasks(path)