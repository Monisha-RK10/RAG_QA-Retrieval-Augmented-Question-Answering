#test_integration.py
import pytest
from app.loader import load_and_chunk_pdf
from app.embeddings import load_or_create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from app.settings import settings

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
def test_query_timeout(monkeypatch):
    # Simulate a slow LLM by patching your query function
    import app.services.llm as llm

    def slow_query(*args, **kwargs):
        import time
        time.sleep(6)  # longer than timeout
        return {"answer": "too slow"}

    monkeypatch.setattr(llm, "query_llm", slow_query)

    response = client.post("/query", json={"question": "What is AI?"})
    # depending on your app logic, might return 408 or 500
    assert response.status_code in (408, 500)
