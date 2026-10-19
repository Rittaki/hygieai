from fastapi.testclient import TestClient

from hygieai_api.config import Settings
from hygieai_api.main import create_app


def test_health_returns_ok() -> None:
    client = TestClient(create_app(Settings(app_env="test")))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_are_disabled_in_production() -> None:
    client = TestClient(create_app(Settings(app_env="production")))

    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404
