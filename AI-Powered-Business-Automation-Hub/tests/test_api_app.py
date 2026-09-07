from fastapi.testclient import TestClient

from src.api.app import app


def test_api_application_metadata_and_openapi():
    client = TestClient(app)

    assert client.get("/health").status_code == 200
    assert app.title == "AI-Powered Business Automation Hub"
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    assert "/tasks" in openapi.json()["paths"]
