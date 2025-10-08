# app/tests/test_api.py

import asyncio
import pytest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from pathlib import Path

from app.fastapi_app import app, DB_DIR, vectordb, qa_chain
from app.loader import load_and_chunk_pdf
from app.embeddings import load_or_create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from app.settings import settings

client = TestClient(app)

# -----------------------------
# Fixture: ensure vectordb + qa_chain exist
# -----------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_vectorstore():
    """
    Runs once per session to ensure vectordb and qa_chain are initialized.
    Avoids 400 Bad Request in /query tests due to missing vectorstore.
    """
    global vectordb, qa_chain
    if not DB_DIR.exists() or not any(DB_DIR.iterdir()):
        chunks = load_and_chunk_pdf(f"{settings.data_dir}/{settings.default_pdf_name}")
        vectordb = load_or_create_vectorstore(chunks, persist_directory=str(DB_DIR))
        qa_chain = build_qa_chain(load_llm(), vectordb)

# -----------------------------
# Test pipeline functions
# -----------------------------
def test_pipeline():
    chunks = load_and_chunk_pdf(f"{settings.data_dir}/{settings.default_pdf_name}")
    assert len(chunks) > 0, "No chunks loaded"

    local_vectordb = load_or_create_vectorstore(chunks, persist_directory="db")
    assert local_vectordb is not None, "Vectorstore creation failed"

    llm = load_llm()
    assert llm is not None, "LLM load failed"

    local_qa_chain = build_qa_chain(llm, local_vectordb)
    result = local_qa_chain({"query": "What is seq2seq model?"})
    print("Test query answer:", result["result"])
    assert result["result"], "QA chain returned empty answer"

# -----------------------------
# Test FastAPI /query timeout
# -----------------------------
def test_query_timeout(monkeypatch):
    def slow_chain(_):
        import time; time.sleep(35)
        return {"result": "This should never return"}

    monkeypatch.setattr("app.fastapi_app.qa_chain", slow_chain)

    response = client.post("/query", json={"question": "Will this timeout?"})
    assert response.status_code == 504
    assert response.json()["detail"] == "Query timed out after 30s"

# -----------------------------
# Test FastAPI /health
# -----------------------------
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# -----------------------------
# Test FastAPI /upload_query
# -----------------------------
def create_valid_pdf(path):
    c = canvas.Canvas(str(path))
    c.drawString(100, 750, "Hello, this is a test PDF.")
    c.save()

def test_upload_query(tmp_path):
    pdf_path = tmp_path / "valid.pdf"
    create_valid_pdf(pdf_path)

    with open(pdf_path, "rb") as f:
        response = client.post(
            "/upload_query",
            files={"file": ("valid.pdf", f, "application/pdf")},
            data={"question": "What is the purpose of this test?"}
        )

    assert response.status_code == 200
    json_resp = response.json()
    print("Upload query response:", json_resp)
    assert "answer" in json_resp
    assert json_resp["answer"], "Empty answer from /upload_query"

# -----------------------------
# Test FastAPI /query endpoint
# -----------------------------
def test_query_endpoint():
    response = client.post("/query", json={"question": "What is the advantage of Index hot-swapping?"})
    assert response.status_code == 200
    print(response.json())

# -----------------------------
# Test config loading
# -----------------------------
def test_settings_load():
    assert settings.llm_model.startswith("google/")
    assert settings.embedding_model.startswith("sentence-transformers/")
    assert settings.data_dir == "data"
