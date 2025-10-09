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
import asyncio
import time

from app.fastapi_app import qa_chain  # patch if needed

@pytest.mark.integration
def test_qa_chain_timeout():
    def slow_chain(query):
        time.sleep(35)
        return {"result": "too slow"}

    # patch qa_chain
    import app.fastapi_app as fa
    fa.qa_chain = slow_chain

    # run wait_for with to_thread
    with pytest.raises(asyncio.TimeoutError):
        asyncio.run(
            asyncio.wait_for(
                asyncio.to_thread(fa.qa_chain, {"query": "What is AI?"}),
                timeout=1  # short timeout for test speed
            )
        )
