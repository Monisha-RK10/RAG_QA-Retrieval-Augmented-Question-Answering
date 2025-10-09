# test_api.py
# Unit & lightweight integration tests for FastAPI app
# ----------------------------------------------------
# test_health          = API health check (unit)
# test_settings_load   = Config parsing test (unit)
# test_query_endpoint  = API + pipeline integration (skipped in CI for now)

import pytest
from fastapi.testclient import TestClient
from app.fastapi_app import app
from app.settings import settings

client = TestClient(app)


# ---------- UNIT TESTS ----------

@pytest.mark.unit
def test_health():
    """FastAPI /health endpoint should return 200 OK and correct JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
