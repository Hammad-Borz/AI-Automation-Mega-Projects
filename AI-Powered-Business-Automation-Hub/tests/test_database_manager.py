from src.models import (
    ActionStatus,
    AutomationAction,
    BusinessTask,
    TaskAnalysis,
    TaskCategory,
    TaskPriority,
)


def test_database_initializes_and_starts_empty(database):
    assert database.database_path.exists()
    assert database.count_tasks() == 0


def test_database_saves_retrieves_and_counts_tasks(database):
    task = BusinessTask(
        task_id="task-1",
        source="api",
        title="Create report",
        content="Create the weekly report.",
        metadata={"priority": "high"},
    )

    database.save_task(task)
    retrieved = database.get_task("task-1")

    assert retrieved == task
    assert database.count_tasks() == 1
    assert database.get_task("missing") is None


def test_database_saves_and_retrieves_analysis(database):
    task = BusinessTask(
        task_id="task-analysis",
        source="test",
        title="Production outage",
        content="The service is unavailable.",
    )
    analysis = TaskAnalysis(
        category=TaskCategory.URGENT,
        priority=TaskPriority.CRITICAL,
        summary="Production outage.",
        confidence=0.98,
        recommended_actions=["Flag as critical"],
    )

    database.save_task(task)
    database.save_analysis(task.task_id, analysis)

    assert database.get_analysis(task.task_id) == analysis


def test_database_saves_and_retrieves_automation_actions(database):
    task = BusinessTask(
        task_id="task-actions",
        source="test",
        title="Action task",
        content="Run actions.",
    )
    actions = [
        AutomationAction(
            action_id="action-1",
            action_type="flag_critical",
            description="Flag task",
            status=ActionStatus.COMPLETED,
            metadata={"execution": "local_demo"},
        )
    ]

    database.save_task(task)
    database.save_actions(task.task_id, actions)

    assert database.get_actions(task.task_id) == actions
