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
    Unit test for /health endpoint with DB connectivity check.
    Returns {"status": "ok", "db": "connected"} if DB/SQLite works.
    """
    response = client.get("/health")
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "ok"
    # tolerate fail if no real DB (CI-safe)
    assert data["db"] in ["connected", "fail"]  


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
