#test_integration.py
import pytest
from app.fastapi_app import app

from app.loader import load_and_chunk_pdf
from app.embeddings import load_or_create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from app.settings import settings

from fastapi.testclient import TestClient
from unittest.mock import patch
import time

client = TestClient(app)

@pytest.mark.integration
def test_full_rag_pipeline():
    chunks = load_and_chunk_pdf(f"{settings.data_dir}/{settings.default_pdf_name}")
    assert chunks, "No chunks loaded from default PDF"

    vectordb = load_or_create_vectorstore(chunks, persist_directory=settings.db_dir)
    llm = load_llm()
    qa_chain = build_qa_chain(llm, vectordb)

    result = qa_chain({"query": "What is seq2seq model?"})
    print("Integration query answer:", result["result"])
    assert result["result"], "RAG pipeline returned empty answer"

@pytest.mark.integration
def test_query_timeout():
    # Patch the qa_chain call to simulate a long-running query
    def slow_qa_chain(*args, **kwargs):
        time.sleep(35)  # longer than 30s timeout
        return {"result": "too slow"}

    with patch("app.fastapi_app.qa_chain", new=slow_qa_chain):
        response = client.post("/query", json={"question": "What is AI?"})
        assert response.status_code == 504
        assert "timed out" in response.json()["detail"]
