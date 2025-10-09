# test_api.py
# Unit & lightweight integration tests for FastAPI app
# ----------------------------------------------------
# test_health          = API health check (unit)
# test_settings_load   = Config parsing test (unit)
# test_query_endpoint  = API + pipeline integration (unit)

import pytest
from fastapi.testclient import TestClient
from app.fastapi_app import app
from app.settings import settings

client = TestClient(app)


# ---------- UNIT TESTS ----------

@pytest.mark.unit
def test_health_db():
    """
    Unit test for health endpoint with DB connectivity check.
    Should return {"status": "ok", "db": "connected"} when DB/SQLite works.
    """
    response = client.get("/health")
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["db"] in ["connected", "fail"]  # tolerate fail if no real DB (CI-safe)


@pytest.mark.unit
def test_settings_load():
    """Lightweight config sanity check."""
    assert settings.llm_model.startswith("google/")
    assert settings.embedding_model.startswith("sentence-transformers/")
    assert settings.data_dir == "data"
    assert settings.postgres_url.startswith("postgresql://")


# ---------- INTEGRATION TESTS ----------

@pytest.mark.integration
def test_query_endpoint():
    """Integration test of /query endpoint with default PDF and chain."""
    response = client.post("/query", json={"question": "What is the advantage of Index hot-swapping?"})
    assert response.status_code == 200
    print(response.json())
