# app/fastapi_app.py
# Production tweak #7: Model caching at startup, load LLM once at startup (FastAPI app startup).
# Production tweak #8: Timeouts for query endpoints.

# tests/test_api.py
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure repo root is in sys.path so "app" package is importable
repo_root = Path(__file__).resolve().parents[1]  # tests/ -> RAG_QA/
sys.path.insert(0, str(repo_root))

from app.fastapi_app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
