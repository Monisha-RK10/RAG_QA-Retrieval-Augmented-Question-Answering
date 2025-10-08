# app/tests/test_api.py
import io
import pytest
from pathlib import Path
from reportlab.pdfgen import canvas

# Do not instantiate TestClient at import time; create via fixture after startup is ready.
from fastapi.testclient import TestClient

# helper to create minimal valid PDF
def create_minimal_pdf_bytes():
    # A tiny valid-like PDF that many parsers tolerate
    return b"%PDF-1.4\n%EOF"

@pytest.fixture(scope="session")
def client():
    """
    Create TestClient as a context manager so startup event runs within the test session.
    """
    from app.fastapi_app import app
    with TestClient(app) as c:
        yield c

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_settings_load():
    # Import settings lazily and do lightweight checks
    from app.settings import settings
    assert isinstance(settings.llm_model, str)
    assert isinstance(settings.embedding_model, str)
    assert isinstance(settings.data_dir, str)

def test_upload_query(client, tmp_path):
    # Create a minimal PDF file on disk and upload it
    pdf_path = tmp_path / "dummy.pdf"
    with open(pdf_path, "wb") as f:
        f.write(create_minimal_pdf_bytes())

    with open(pdf_path, "rb") as f:
        r = client.post(
            "/upload_query",
            files={"file": ("dummy.pdf", f, "application/pdf")},
            data={"question": "what is this?"}
        )

    assert r.status_code == 200
    json_r = r.json()
    assert "answer" in json_r

def test_query_mock(client):
    r = client.post("/query", json={"question": "hi?"})
    assert r.status_code == 200
    assert "answer" in r.json()
