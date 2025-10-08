from fastapi.testclient import TestClient
from app.fastapi_app import app

client = TestClient(app)

def test_health():
    """Basic health check to confirm FastAPI app is running."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
