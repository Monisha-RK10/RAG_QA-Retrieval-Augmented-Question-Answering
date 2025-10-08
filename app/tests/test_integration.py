import pytest
from app.loader import load_and_chunk_pdf
from app.embeddings import load_or_create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from app.settings import settings

from fastapi.testclient import TestClient  
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
