import pytest
from fastapi.testclient import TestClient

from src.api.app import app
from src.api.dependencies import get_database_manager, get_workflow
from src.api.dependencies import get_analytics_service
from src.analytics import AnalyticsService
from src.database_manager import DatabaseManager
from src.workflow import Workflow


@pytest.fixture
def api_client(database):
    app.dependency_overrides[get_database_manager] = lambda: database
    app.dependency_overrides[get_workflow] = lambda: Workflow(database)
    app.dependency_overrides[get_analytics_service] = lambda: AnalyticsService(database)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_health_endpoint(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "AI-Powered Business Automation Hub",
    }


def test_create_task_uses_existing_workflow(api_client, database):
    response = api_client.post(
        "/tasks",
        json={
            "task_id": "api-task-1",
            "title": "Customer cannot access account",
            "content": "Please help reset the password.",
            "source": "api",
            "metadata": {"customer_id": "customer-1"},
        },
    )

    body = response.json()
    assert response.status_code == 201
    assert body["task_id"] == "api-task-1"
    assert body["source"] == "api"
    assert body["analysis"]["category"] == "support"
    assert body["planned_actions"]
    assert body["execution_results"]
    assert body["final_status"] == "completed"
    assert database.get_task("api-task-1") is not None


def test_create_task_generates_id_when_omitted(api_client):
    response = api_client.post(
        "/tasks",
        json={"title": "General request", "content": "Please review this request."},
    )

    assert response.status_code == 201
    assert response.json()["task_id"].startswith("api-")


def test_create_task_rejects_invalid_request(api_client):
    response = api_client.post("/tasks", json={"title": "Missing content"})

    assert response.status_code == 422
    assert response.json()["error"] == "request_validation_error"
    assert "Traceback" not in response.text


def test_batch_endpoint_processes_multiple_tasks(api_client):
    response = api_client.post(
        "/tasks/batch",
        json=[
            {"task_id": "batch-1", "title": "First", "content": "First content"},
            {"task_id": "batch-2", "title": "Second", "content": "Second content"},
        ],
    )

    assert response.status_code == 201
    assert [item["task_id"] for item in response.json()["results"]] == ["batch-1", "batch-2"]


def test_batch_endpoint_rejects_malformed_request(api_client):
    response = api_client.post(
        "/tasks/batch",
        json=[{"task_id": "batch-1", "title": "Missing content"}],
    )

    assert response.status_code == 422
    assert response.json()["error"] == "request_validation_error"


def test_get_task_returns_persisted_information(api_client):
    created = api_client.post(
        "/tasks",
        json={
            "task_id": "stored-1",
            "title": "Sales pricing request",
            "content": "A prospect requests a quote.",
            "source": "api",
        },
    )
    assert created.status_code == 201

    response = api_client.get("/tasks/stored-1")

    assert response.status_code == 200
    assert response.json()["task_id"] == "stored-1"
    assert response.json()["title"] == "Sales pricing request"
    assert response.json()["analysis"]["category"] == "sales"
    assert response.json()["execution_results"]


def test_get_unknown_task_returns_404(api_client):
    response = api_client.get("/tasks/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_duplicate_submission_returns_conflict(api_client):
    payload = {
        "task_id": "duplicate-api-1",
        "title": "Duplicate API task",
        "content": "Process once.",
    }
    assert api_client.post("/tasks", json=payload).status_code == 201

    response = api_client.post("/tasks", json=payload)

    assert response.status_code == 409
    assert response.json() == {
        "error": "duplicate_task",
        "detail": "A task with this ID already exists.",
    }
    assert "Traceback" not in response.text


def test_batch_duplicate_returns_failed_item_and_continues(api_client):
    existing = {"task_id": "batch-existing", "title": "Existing", "content": "Already stored."}
    assert api_client.post("/tasks", json=existing).status_code == 201

    response = api_client.post(
        "/tasks/batch",
        json=[
            existing,
            {"task_id": "batch-new", "title": "New", "content": "Process this one."},
        ],
    )

    assert response.status_code == 201
    results = response.json()["results"]
    assert results[0]["final_status"] == "failed"
    assert results[0]["error"] == "Task could not be processed."
    assert results[1]["final_status"] == "completed"


def test_get_task_returns_processing_metadata(api_client):
    response = api_client.post(
        "/tasks",
        json={"task_id": "metadata-1", "title": "Metadata", "content": "Store timing."},
    )
    assert response.status_code == 201

    stored = api_client.get("/tasks/metadata-1")

    assert stored.status_code == 200
    assert stored.json()["processing_metadata"]["lifecycle_status"] == "completed"
    assert stored.json()["processing_metadata"]["processing_duration_ms"] >= 0


def test_analytics_endpoints_return_structured_results(api_client):
    api_client.post(
        "/tasks",
        json={
            "task_id": "analytics-api-1",
            "title": "Customer requests pricing",
            "content": "Please provide a quote.",
            "source": "api",
        },
    )

    overview = api_client.get("/analytics/overview")
    performance = api_client.get("/analytics/performance")
    integrations = api_client.get("/analytics/integrations")
    recent = api_client.get("/analytics/recent?limit=1")

    assert overview.status_code == 200
    assert overview.json()["total_tasks"] == 1
    assert performance.status_code == 200
    assert performance.json()["tasks_with_duration"] == 1
    assert integrations.status_code == 200
    assert integrations.json()["total_events"] == 1
    assert recent.status_code == 200
    assert len(recent.json()["items"]) == 1


def test_analytics_recent_limit_is_bounded(api_client):
    response = api_client.get("/analytics/recent?limit=10000")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 0
