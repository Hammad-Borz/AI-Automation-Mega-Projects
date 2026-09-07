"""SQLite persistence for automation tasks."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings
from .exceptions import DatabaseError
from .models import (
    AutomationAction,
    AutomationExecutionResult,
    AutomationResult,
    BusinessTask,
    ProcessingMetadata,
    TaskAnalysis,
)


class DatabaseManager:
    """Manage the Phase 1 SQLite database."""

    def __init__(self, settings: Settings | None = None, database_path: Path | None = None) -> None:
        self.settings = settings or Settings()
        self.database_path = Path(database_path or self.settings.database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        """Create the automation task table if it does not exist."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS automation_tasks (
                        task_id TEXT PRIMARY KEY,
                        source TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS task_processing (
                        task_id TEXT PRIMARY KEY,
                        lifecycle_status TEXT NOT NULL,
                        processing_started_at TEXT,
                        processing_completed_at TEXT,
                        processing_duration_ms REAL,
                        failure_message TEXT,
                        planned_actions TEXT NOT NULL,
                        execution_result TEXT,
                        integration_results TEXT NOT NULL,
                        FOREIGN KEY (task_id) REFERENCES automation_tasks(task_id)
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS task_analyses (
                        task_id TEXT PRIMARY KEY,
                        category TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        summary TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        recommended_actions TEXT NOT NULL,
                        FOREIGN KEY (task_id) REFERENCES automation_tasks(task_id)
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS automation_actions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_id TEXT NOT NULL,
                        action_id TEXT NOT NULL,
                        action_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        status TEXT NOT NULL,
                        execution_metadata TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (task_id) REFERENCES automation_tasks(task_id)
                    )
                    """
                )
        except sqlite3.Error as error:
            raise DatabaseError(f"Could not initialize database: {error}") from error

    def save_task(self, task: BusinessTask) -> None:
        """Insert or replace a business task."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO automation_tasks
                    (task_id, source, title, content, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task.task_id,
                        task.source,
                        task.title,
                        task.content,
                        json.dumps(task.metadata),
                        task.created_at.isoformat(),
                    ),
                )
        except (sqlite3.Error, TypeError, ValueError) as error:
            raise DatabaseError(f"Could not save task '{task.task_id}': {error}") from error

    def task_exists(self, task_id: str) -> bool:
        """Return whether a task ID is already persisted."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                row = connection.execute(
                    "SELECT 1 FROM automation_tasks WHERE task_id = ? LIMIT 1", (task_id,)
                ).fetchone()
            return row is not None
        except sqlite3.Error as error:
            raise DatabaseError("Could not check task existence.") from error

    def save_processing(
        self,
        task_id: str,
        processing: ProcessingMetadata,
        planned_actions: list[AutomationAction] | None = None,
        execution_result: AutomationExecutionResult | None = None,
    ) -> None:
        """Persist lifecycle, timing, and processing result details."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO task_processing
                    (task_id, lifecycle_status, processing_started_at, processing_completed_at,
                     processing_duration_ms, failure_message, planned_actions, execution_result,
                     integration_results)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task_id,
                        processing.lifecycle_status.value,
                        processing.processing_started_at.isoformat() if processing.processing_started_at else None,
                        processing.processing_completed_at.isoformat() if processing.processing_completed_at else None,
                        processing.processing_duration_ms,
                        processing.failure_message,
                        json.dumps([self._model_data(action) for action in planned_actions or []]),
                        json.dumps(self._model_data(execution_result)) if execution_result else None,
                        json.dumps(
                            [self._model_data(item) for item in execution_result.integration_results]
                            if execution_result
                            else []
                        ),
                    ),
                )
        except (sqlite3.Error, TypeError, ValueError) as error:
            raise DatabaseError(f"Could not save processing information for '{task_id}'.") from error

    def get_task_record(self, task_id: str) -> dict | None:
        """Return all persisted task-processing information for one task."""
        task = self.get_task(task_id)
        if task is None:
            return None
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.row_factory = sqlite3.Row
                row = connection.execute(
                    "SELECT * FROM task_processing WHERE task_id = ?", (task_id,)
                ).fetchone()
            processing = None
            planned_actions: list[AutomationAction] = []
            execution_result = None
            if row is not None:
                processing = ProcessingMetadata(
                    lifecycle_status=row["lifecycle_status"],
                    processing_started_at=row["processing_started_at"],
                    processing_completed_at=row["processing_completed_at"],
                    processing_duration_ms=row["processing_duration_ms"],
                    failure_message=row["failure_message"],
                )
                planned_actions = [AutomationAction(**item) for item in json.loads(row["planned_actions"])]
                if row["execution_result"]:
                    execution_result = AutomationExecutionResult(**json.loads(row["execution_result"]))
            return {
                "task": task,
                "analysis": self.get_analysis(task_id),
                "planned_actions": planned_actions,
                "execution_result": execution_result,
                "processing_metadata": processing or ProcessingMetadata(),
            }
        except (sqlite3.Error, TypeError, ValueError, json.JSONDecodeError) as error:
            raise DatabaseError("Could not retrieve task processing information.") from error

    @staticmethod
    def _model_data(value):
        """Serialize a Pydantic model across supported Pydantic versions."""
        if value is None:
            return None
        if hasattr(value, "model_dump"):
            try:
                return value.model_dump(mode="json")
            except TypeError:
                return value.model_dump()
        return value.dict()

    def save_analysis(self, task_id: str, analysis: TaskAnalysis) -> None:
        """Store or replace analysis associated with a task."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO task_analyses
                    (task_id, category, priority, summary, confidence, recommended_actions)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task_id,
                        analysis.category.value,
                        analysis.priority.value,
                        analysis.summary,
                        analysis.confidence,
                        json.dumps(analysis.recommended_actions),
                    ),
                )
        except (sqlite3.Error, TypeError, ValueError) as error:
            raise DatabaseError(f"Could not save analysis for task '{task_id}': {error}") from error

    def get_analysis(self, task_id: str) -> TaskAnalysis | None:
        """Retrieve analysis for a task, or return None when it is absent."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.row_factory = sqlite3.Row
                row = connection.execute(
                    "SELECT * FROM task_analyses WHERE task_id = ?", (task_id,)
                ).fetchone()
            if row is None:
                return None
            return TaskAnalysis(
                category=row["category"],
                priority=row["priority"],
                summary=row["summary"],
                confidence=row["confidence"],
                recommended_actions=json.loads(row["recommended_actions"]),
            )
        except (sqlite3.Error, TypeError, ValueError, json.JSONDecodeError) as error:
            raise DatabaseError(f"Could not retrieve analysis for task '{task_id}': {error}") from error

    def save_actions(self, task_id: str, actions: list[AutomationAction]) -> None:
        """Replace persisted execution actions for a task."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.execute("DELETE FROM automation_actions WHERE task_id = ?", (task_id,))
                connection.executemany(
                    """
                    INSERT INTO automation_actions
                    (task_id, action_id, action_type, description, status, execution_metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            task_id,
                            action.action_id,
                            action.action_type,
                            action.description,
                            action.status.value,
                            json.dumps(action.metadata),
                            datetime.now(timezone.utc).isoformat(),
                        )
                        for action in actions
                    ],
                )
        except (sqlite3.Error, TypeError, ValueError) as error:
            raise DatabaseError(f"Could not save actions for task '{task_id}': {error}") from error

    def get_actions(self, task_id: str) -> list[AutomationAction]:
        """Retrieve persisted execution actions for a task."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.row_factory = sqlite3.Row
                rows = connection.execute(
                    "SELECT * FROM automation_actions WHERE task_id = ? ORDER BY id", (task_id,)
                ).fetchall()
            return [
                AutomationAction(
                    action_id=row["action_id"],
                    action_type=row["action_type"],
                    description=row["description"],
                    status=row["status"],
                    metadata=json.loads(row["execution_metadata"]),
                )
                for row in rows
            ]
        except (sqlite3.Error, TypeError, ValueError, json.JSONDecodeError) as error:
            raise DatabaseError(f"Could not retrieve actions for task '{task_id}': {error}") from error

    def get_task(self, task_id: str) -> BusinessTask | None:
        """Retrieve a task by ID, or return None when it is absent."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.row_factory = sqlite3.Row
                row = connection.execute(
                    "SELECT * FROM automation_tasks WHERE task_id = ?", (task_id,)
                ).fetchone()
            if row is None:
                return None
            return BusinessTask(
                task_id=row["task_id"],
                source=row["source"],
                title=row["title"],
                content=row["content"],
                metadata=json.loads(row["metadata"]),
                created_at=row["created_at"],
            )
        except (sqlite3.Error, TypeError, ValueError, json.JSONDecodeError) as error:
            raise DatabaseError(f"Could not retrieve task '{task_id}': {error}") from error

    def count_tasks(self) -> int:
        """Return the number of stored tasks."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                row = connection.execute("SELECT COUNT(*) FROM automation_tasks").fetchone()
            return int(row[0])
        except sqlite3.Error as error:
            raise DatabaseError(f"Could not count tasks: {error}") from error

    def get_analytics_task_rows(self) -> list[dict]:
        """Return one lightweight joined row per task for overview analytics."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.row_factory = sqlite3.Row
                rows = connection.execute(
                    """
                    SELECT t.source, t.created_at,
                           a.category, a.priority,
                           COALESCE(p.lifecycle_status, 'received') AS status
                    FROM automation_tasks AS t
                    LEFT JOIN task_analyses AS a ON a.task_id = t.task_id
                    LEFT JOIN task_processing AS p ON p.task_id = t.task_id
                    """
                ).fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as error:
            raise DatabaseError("Could not load overview analytics.") from error

    def get_processing_metric_rows(self) -> list[dict]:
        """Return persisted processing durations for analytics."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.row_factory = sqlite3.Row
                rows = connection.execute(
                    "SELECT processing_duration_ms AS duration_ms FROM task_processing"
                ).fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as error:
            raise DatabaseError("Could not load processing analytics.") from error

    def get_persisted_integration_results(self) -> list[dict]:
        """Return integration results that were actually persisted."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                rows = connection.execute(
                    "SELECT integration_results FROM task_processing"
                ).fetchall()
            results = []
            for (serialized,) in rows:
                if serialized:
                    results.extend(json.loads(serialized))
            return results
        except (sqlite3.Error, TypeError, ValueError, json.JSONDecodeError) as error:
            raise DatabaseError("Could not load integration analytics.") from error

    def get_recent_activity(self, limit: int) -> list[dict]:
        """Return newest task activity with persisted analysis/lifecycle fields."""
        try:
            with sqlite3.connect(self.database_path) as connection:
                connection.row_factory = sqlite3.Row
                rows = connection.execute(
                    """
                    SELECT t.task_id, t.source, t.created_at,
                           a.category, a.priority,
                           COALESCE(p.lifecycle_status, 'received') AS status,
                           p.processing_completed_at AS processed_at
                    FROM automation_tasks AS t
                    LEFT JOIN task_analyses AS a ON a.task_id = t.task_id
                    LEFT JOIN task_processing AS p ON p.task_id = t.task_id
                    ORDER BY COALESCE(p.processing_completed_at, t.created_at) DESC, t.task_id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as error:
            raise DatabaseError("Could not load recent activity.") from error
