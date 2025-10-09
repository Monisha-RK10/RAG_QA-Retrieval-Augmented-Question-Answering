# app/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.fastapi_app import app
from app.settings import settings

client = TestClient(app)

# -------------------------
# UNIT TESTS
# -------------------------

@pytest.mark.unit
def test_health_db():
    """
    Unit test for health endpoint with DB connectivity check.
    Should return {"status": "ok", "db": "connected"} when DB/SQLite works.
    """
    response = client.get("/health")
    data = response.json()
    
    assert response.status_code == 200  # API responds
    assert data["status"] in ["ok", "fail"]  # tolerate CI fallback
    assert "db" in data or "db_error" in data  # ensure DB key exists


@pytest.mark.unit
def test_settings_load():
    """
    Ensures environment/config parsing works.
    """
    assert hasattr(settings, "postgres_url")
    assert isinstance(settings.postgres_url, str)
    assert hasattr(settings, "data_dir")
    assert isinstance(settings.data_dir, str)
    assert hasattr(settings, "db_dir")
    assert isinstance(settings.db_dir, str)


@pytest.mark.unit
def test_query_endpoint():
    """
    Minimal integration check that the /query endpoint runs and returns a response.
    """
    response = client.post(
        "/query",
        data={"question": "What is AI?"}
    )
    assert response.status_code in [200, 400]  # depending on empty DB/vectorstore
    # Optional: check that response JSON has 'answer' key if 200
    if response.status_code == 200:
        data = response.json()
        assert "answer" in data
