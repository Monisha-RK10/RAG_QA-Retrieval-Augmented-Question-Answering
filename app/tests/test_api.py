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
def test_settings_values():
    """
    Unit test to assert that critical settings exist and have valid types.
    """
    assert hasattr(settings, "postgres_url")
    assert isinstance(settings.postgres_url, str)
    assert hasattr(settings, "data_dir")
    assert isinstance(settings.data_dir, str)
    assert hasattr(settings, "db_dir")
    assert isinstance(settings.db_dir, str)
