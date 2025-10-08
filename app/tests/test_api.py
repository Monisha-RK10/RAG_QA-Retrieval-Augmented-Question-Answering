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

@pytest.fixture(scope="session", autouse=True)
def setup_vectorstore():
    global vectordb, qa_chain
    if not DB_DIR.exists() or not any(DB_DIR.iterdir()):
        chunks = load_and_chunk_pdf("data/RAG_Paper.pdf")
        vectordb = load_or_create_vectorstore(chunks, persist_directory=str(DB_DIR))
        qa_chain = build_qa_chain(load_llm(), vectordb)
     
client = TestClient(app)

# Test FastAPI /health endpoint
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# Lightweight “config test” to know if config parsing breaks in the future
def test_settings_load():
    assert settings.llm_model.startswith("google/")
    assert settings.embedding_model.startswith("sentence-transformers/")
    assert settings.data_dir == "data"

