# app/tests/test_api.py
# Unit & lightweight integration tests for FastAPI app
# ----------------------------------------------------
# test_health        = Basic health check of FastAPI + DB connection (unit)
# test_settings_load = Config sanity check (unit)

import pytest
from fastapi.testclient import TestClient
from app.fastapi_app import app
from app.settings import settings

client = TestClient(app)                                                                    # Effectively makes the tests behave like real HTTP requests but run entirely in Python memory.

# ---------- UNIT TESTS ----------

@pytest.mark.unit
def test_health_db():                                                                       # Pytest detects all functions prefixed with test_
    response = client.get("/health")
    data = response.json()
    assert response.status_code == 200
    assert data["status"] in ["ok", "fail"]
    assert "db" in data or "db_error" in data

@pytest.mark.unit
def test_settings_load():
    assert settings.llm_model.startswith("google/")
    assert settings.embedding_model.startswith("sentence-transformers/")
    assert settings.data_dir == "data"
    assert settings.postgres_url.startswith("postgresql://")

