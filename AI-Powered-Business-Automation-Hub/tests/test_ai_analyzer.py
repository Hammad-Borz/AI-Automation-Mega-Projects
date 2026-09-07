import pytest

from src.ai_analyzer import AIAnalyzer
from src.models import BusinessTask, TaskCategory, TaskPriority


@pytest.fixture
def analyzer(settings):
    return AIAnalyzer(settings)


def make_task(title, content):
    return BusinessTask(task_id="analysis-1", source="test", title=title, content=content)


def test_analyzer_classifies_urgent_task(analyzer):
    analysis = analyzer.analyze(
        make_task("Production checkout outage", "The payment system is unavailable and needs an emergency response.")
    )

    assert analysis.category is TaskCategory.URGENT
    assert analysis.priority is TaskPriority.CRITICAL
    assert analysis.recommended_actions == [
        "Flag as critical",
        "Notify operations team",
        "Create incident record",
    ]


def test_analyzer_classifies_support_task(analyzer):
    analysis = analyzer.analyze(make_task("Customer support request", "The customer cannot reset their password."))

    assert analysis.category is TaskCategory.SUPPORT
    assert analysis.priority is TaskPriority.MEDIUM


def test_analyzer_classifies_sales_task(analyzer):
    analysis = analyzer.analyze(make_task("Enterprise pricing inquiry", "A prospect requests a quote and demo."))

    assert analysis.category is TaskCategory.SALES
    assert analysis.priority is TaskPriority.MEDIUM


def test_analyzer_classifies_billing_task(analyzer):
    analysis = analyzer.analyze(make_task("Duplicate invoice charge", "Please review this billing payment and refund it."))

    assert analysis.category is TaskCategory.BILLING
    assert analysis.priority is TaskPriority.MEDIUM


def test_analyzer_confidence_is_in_range_and_summary_is_concise(analyzer):
    analysis = analyzer.analyze(make_task("Review request", "Please review this general business request."))

    assert 0.0 <= analysis.confidence <= 1.0
    assert analysis.summary == "Review request."
    assert analysis.recommended_actions


def test_demo_analysis_is_deterministic(analyzer):
    task = make_task("Check inventory operations", "Review the inventory workflow.")

    assert analyzer.analyze(task) == analyzer.analyze(task)
