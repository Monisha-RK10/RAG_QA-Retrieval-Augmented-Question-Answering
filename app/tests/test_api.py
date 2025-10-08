# app/tests/test_api.py
import asyncio
import pytest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from pathlib import Path
from unittest.mock import patch

from app.fastapi_app import app, DATA_DIR, DB_DIR, vectordb, qa_chain
from app.settings import settings

client = TestClient(app)

# -----------------------------
# Helper: create a minimal dummy PDF
# -----------------------------
def create_dummy_pdf(path):
    c = canvas.Canvas(str(path))
    c.drawString(100, 750, "Hello CI test PDF")
    c.save()

# -----------------------------
# Test /health endpoint
# -----------------------------
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# -----------------------------
# Test /upload_query endpoint
# -----------------------------
def test_upload_query(tmp_path):
    pdf_path = tmp_path / "dummy.pdf"
    create_dummy_pdf(pdf_path)

    with open(pdf_path, "rb") as f:
        response = client.post(
            "/upload_query",
            files={"file": ("dummy.pdf", f, "application/pdf")},
            data={"question": "What is this PDF?"}
        )

    assert response.status_code == 200
    json_resp = response.json()
    assert "answer" in json_resp
    assert json_resp["answer"], "Empty answer from /upload_query"

# -----------------------------
# Test /query endpoint (mock vectorstore & chain)
# -----------------------------
@pytest.fixture(autouse=True)
def mock_chain():
    """
    Mock QA chain and vectorstore so /query works without a real PDF.
    """
    with patch("app.fastapi_app.vectordb", new=True), \
         patch("app.fastapi_app.qa_chain") as mock_qa:
        mock_qa.return_value = {"result": "Mocked answer"}
        yield

def test_query():
    response = client.post("/query", json={"question": "Test query?"})
    assert response.status_code == 200
    assert response.json() == {"answer": "Mocked answer"}
