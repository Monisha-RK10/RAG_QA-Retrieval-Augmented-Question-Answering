# app/tests/test_api.py
import io
from fastapi.testclient import TestClient
from app.fastapi_app import app
from app.settings import settings

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_settings_load():
    # just check that config values exist and are strings
    assert isinstance(settings.llm_model, str) and settings.llm_model
    assert isinstance(settings.embedding_model, str) and settings.embedding_model
    assert isinstance(settings.data_dir, str) and settings.data_dir

def test_upload_query():
    dummy_pdf = io.BytesIO(b"%PDF-1.4\n%EOF")
    r = client.post(
        "/upload_query",
        files={"file": ("dummy.pdf", dummy_pdf, "application/pdf")},
        data={"question": "hello?"}
    )
    assert r.status_code == 200
    assert "answer" in r.json()

def test_query_mock():
    r = client.post("/query", json={"question": "what is up?"})
    assert r.status_code == 200
    assert "answer" in r.json()
