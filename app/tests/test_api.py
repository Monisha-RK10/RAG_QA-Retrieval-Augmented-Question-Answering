# app/tests/test_api.py
import sys
from pathlib import Path

# Add repo root to sys.path (GitHub Actions needs this)
repo_root = Path(__file__).resolve().parents[2]  # adjust to go up 2 levels from tests/
sys.path.insert(0, str(repo_root))

from fastapi.testclient import TestClient
from app.fastapi_app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
