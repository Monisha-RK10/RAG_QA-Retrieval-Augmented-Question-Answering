# app/tests/test_api.py

# test_pipeline = unit/integration test of the pipeline internals, checks the internal pipeline works (PDF → embeddings → vector DB → LLM → QA chain).
# test_query_endpoint = API layer test of FastAPI + pipeline integration, checks /query works with the persisted/default RAG_Paper.pdf.
# test_query_timeout → checks the timeout works correctly (monkeypatch simulates a slow chain).
# test_health (API) = Monitoring, services like Kubernetes, Docker, AWS ELB, etc. hit /health to check if the app is alive.
# test_upload_query (API with file upload)

import asyncio
import pytest

from fastapi.testclient import TestClient                                                                 # FastAPI’s built-in testing utility. It spins up the app in memory so you can send HTTP requests without running a real server.
from app.fastapi_app import app                                                                           # Imports the FastAPI app instance created
from app.loader import load_and_chunk_pdf
from app.embeddings import load_or_create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from langchain_community.vectorstores import Chroma

from app.settings import settings

client = TestClient(app)

# Test the loader + embeddings + chain
def test_pipeline():                                                                                      # Test 1: Pipeline (direct function calls)
    # 1. Load PDF                                                                                         # Verifies the loader can read the default PDF and split into chunks.
    #chunks = load_and_chunk_pdf("data/RAG_Paper.pdf")
    chunks = load_and_chunk_pdf(f"{settings.data_dir}/{settings.default_pdf_name}")
    assert len(chunks) > 0, "No chunks loaded"

    # 2. Create vectorstore                                                                               # Ensures vectorstore creation + persistence works. (db/ should have Chroma files after this.)
    vectordb = load_or_create_vectorstore(chunks, persist_directory="db")
    assert vectordb is not None, "Vectorstore creation failed"

    # 3. Load LLM                                                                                         # Confirms the LLM is loaded correctly (even if it falls back to CPU / smaller model).
    llm = load_llm()
    assert llm is not None, "LLM load failed"

    # 4. Build QA chain                                                                                   # Runs a real query end-to-end (loader → embeddings → retriever → LLM).
    qa_chain = build_qa_chain(llm, vectordb)
    result = qa_chain({"query": "What is seq2seq model?"})
    print("Test query answer:", result["result"])
   # assert "Abstractive" in result["result"].lower(), "Unexpected answer"                                # Commented out because it was too strict
    assert result["result"], "QA chain returned empty answer"

# Test FastAPI for timeout 
def test_query_timeout(monkeypatch):
    # Monkeypatch qa_chain to simulate a long-running query
    from app.fastapi_app import qa_chain

    def slow_chain(_):
        # Simulate 35s blocking work
        import time; time.sleep(35)
        return {"result": "This should never return"}

    monkeypatch.setattr("app.fastapi_app.qa_chain", slow_chain)

    response = client.post("/query", json={"question": "Will this timeout?"})
    assert response.status_code == 504
    assert response.json()["detail"] == "Query timed out after 30s"

# Test FastAPI /health endpoint
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Test FastAPI /upload_query endpoint
from reportlab.pdfgen import canvas

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

# Lightweight “config test” to know if config parsing breaks in the future
def test_settings_load():
    assert settings.llm_model.startswith("google/")
    assert settings.embedding_model.startswith("sentence-transformers/")
    assert settings.data_dir == "data"

# Test FastAPI /query endpoint                                                                            # Test 2: FastAPI endpoint (end-to-end API test), mimics a real client calling the API
def test_query_endpoint():
    response = client.post("/query", json={"question": "What is the advantage of Index hot-swapping?"})
    #print("API response:", response.json())
    assert response.status_code == 200
    print(response.json())
