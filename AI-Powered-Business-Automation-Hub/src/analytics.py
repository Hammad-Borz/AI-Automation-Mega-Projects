"""Operational analytics built on persisted automation data."""

from collections import Counter
from statistics import mean
from typing import Any

from pydantic import BaseModel, Field

from .database_manager import DatabaseManager


class MetricCounts(BaseModel):
    """Counts grouped by a single dimension."""

    counts: dict[str, int] = Field(default_factory=dict)


class OverviewAnalytics(BaseModel):
    """High-level task and outcome metrics."""

    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    received_tasks: int
    processing_tasks: int
    completion_rate: float
    failure_rate: float
    tasks_by_source: dict[str, int] = Field(default_factory=dict)
    tasks_by_category: dict[str, int] = Field(default_factory=dict)
    tasks_by_priority: dict[str, int] = Field(default_factory=dict)


class PerformanceAnalytics(BaseModel):
    """Processing duration metrics in seconds."""

    duration_unit: str = "seconds"
    tasks_with_duration: int
    average_duration: float | None = None
    minimum_duration: float | None = None
    maximum_duration: float | None = None


class IntegrationAnalytics(BaseModel):
    """Counts of persisted connector results."""

    total_events: int
    by_integration: dict[str, int] = Field(default_factory=dict)
    by_status: dict[str, int] = Field(default_factory=dict)


class RecentActivity(BaseModel):
    """A concise recent task activity item."""

    task_id: str
    source: str
    category: str | None = None
    priority: str | None = None
    status: str
    created_at: str
    processed_at: str | None = None


class AnalyticsService:
    """Compute operational metrics without exposing database details to routes."""

    MAX_RECENT_LIMIT = 100

    def __init__(self, database: DatabaseManager) -> None:
        self.database = database

    def overview(self) -> OverviewAnalytics:
        """Return task counts, rates, and grouped dimensions."""
        rows = self.database.get_analytics_task_rows()
        statuses = Counter(row["status"] for row in rows)
        total = len(rows)
        return OverviewAnalytics(
            total_tasks=total,
            completed_tasks=statuses["completed"],
            failed_tasks=statuses["failed"],
            received_tasks=statuses["received"],
            processing_tasks=statuses["processing"],
            completion_rate=self._rate(statuses["completed"], total),
            failure_rate=self._rate(statuses["failed"], total),
            tasks_by_source=dict(Counter(row["source"] for row in rows)),
            tasks_by_category=dict(Counter(row["category"] for row in rows if row["category"])),
            tasks_by_priority=dict(Counter(row["priority"] for row in rows if row["priority"])),
        )

    def performance(self) -> PerformanceAnalytics:
        """Return duration metrics for records that contain timing data."""
        durations = [
            float(row["duration_ms"]) / 1000
            for row in self.database.get_processing_metric_rows()
            if row["duration_ms"] is not None
        ]
        return PerformanceAnalytics(
            tasks_with_duration=len(durations),
            average_duration=mean(durations) if durations else None,
            minimum_duration=min(durations) if durations else None,
            maximum_duration=max(durations) if durations else None,
        )

    def integrations(self) -> IntegrationAnalytics:
        """Return counts for persisted integration result events only."""
        events = self.database.get_persisted_integration_results()
        return IntegrationAnalytics(
            total_events=len(events),
            by_integration=dict(Counter(event.get("integration_name", "unknown") for event in events)),
            by_status=dict(Counter(event.get("status", "unknown") for event in events)),
        )

    def recent(self, limit: int = 20) -> list[RecentActivity]:
        """Return newest activity, bounded to a safe maximum."""
        safe_limit = min(max(limit, 1), self.MAX_RECENT_LIMIT)
        return [RecentActivity(**row) for row in self.database.get_recent_activity(safe_limit)]

    @staticmethod
    def _rate(value: int, total: int) -> float:
        return round(value / total * 100, 2) if total else 0.0