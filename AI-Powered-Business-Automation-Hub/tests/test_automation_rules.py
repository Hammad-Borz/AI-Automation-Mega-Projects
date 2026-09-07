from src.automation_rules import AutomationRulesEngine
from src.models import TaskAnalysis, TaskCategory, TaskPriority


def make_analysis(category, priority=TaskPriority.MEDIUM):
    return TaskAnalysis(
        category=category,
        priority=priority,
        summary="Task summary.",
        confidence=0.9,
    )


def test_critical_urgent_tasks_get_incident_actions():
    actions = AutomationRulesEngine().plan_actions(
        make_analysis(TaskCategory.URGENT, TaskPriority.CRITICAL)
    )

    assert [action.action_type for action in actions] == [
        "flag_critical",
        "create_incident_record",
        "prepare_operations_notification",
    ]


def test_category_rules_produce_expected_actions():
    engine = AutomationRulesEngine()

    assert [a.action_type for a in engine.plan_actions(make_analysis(TaskCategory.SUPPORT))] == [
        "assign_support_queue", "prepare_customer_response"
    ]
    assert [a.action_type for a in engine.plan_actions(make_analysis(TaskCategory.SALES))] == [
        "assign_sales_team", "create_sales_follow_up"
    ]
    assert [a.action_type for a in engine.plan_actions(make_analysis(TaskCategory.BILLING))] == [
        "assign_billing_review", "prepare_billing_response"
    ]
    assert [a.action_type for a in engine.plan_actions(make_analysis(TaskCategory.GENERAL))] == [
        "mark_for_general_review"
    ]


def test_rules_are_deterministic():
    analysis = make_analysis(TaskCategory.OPERATIONS, TaskPriority.HIGH)
    engine = AutomationRulesEngine()

    assert engine.plan_actions(analysis) == engine.plan_actions(analysis)
