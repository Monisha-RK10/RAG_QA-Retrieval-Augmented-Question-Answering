#test_integration.py
import pytest
from app.fastapi_app import app

from app.loader import load_and_chunk_pdf
from app.embeddings import load_or_create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from app.settings import settings

#from fastapi.testclient import TestClient
from unittest.mock import patch
import time

#client = TestClient(app)

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

import pytest
from httpx import AsyncClient
from app.fastapi_app import app
import asyncio

@pytest.mark.integration
@pytest.mark.anyio
async def test_query_timeout_async(monkeypatch):
    async def slow_qa_chain(*args, **kwargs):
        await asyncio.sleep(35)
        return {"result": "too slow"}

    # Patch the global qa_chain to our slow async function
    import app.fastapi_app as fa
    fa.qa_chain = slow_qa_chain

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/query", json={"question": "What is AI?"})
        assert response.status_code == 504
        assert "timed out" in response.json()["detail"]
