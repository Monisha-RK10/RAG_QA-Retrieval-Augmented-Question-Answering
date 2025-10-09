#test_integration.py
# Integration tests for FastAPI app
# ----------------------------------------------------
# test_full_rag_pipeline  = Real end-to-end RAG check (integration) to assert that the answer is not empty
# test_qa_chain_timeout   = Time out test (integartion) to assert that the timeout occurs


import pytest
from app.fastapi_app import app

from app.loader import load_and_chunk_pdf
from app.embeddings import load_or_create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from app.settings import settings

#from unittest.mock import patch
import time
import asyncio
from app.fastapi_app import qa_chain                                                         # patch if needed

# ---------- INTEGRATION TESTS ----------

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
def test_qa_chain_timeout():
    def slow_chain(query):
        time.sleep(35)
        return {"result": "too slow"}

    # patch qa_chain
    import app.fastapi_app as fa
    original_qa_chain = fa.qa_chain
    fa.qa_chain = slow_chain
    
    # run wait_for with to_thread
    try:
        with pytest.raises(asyncio.TimeoutError):                                            # test just checks that TimeoutError is raised, pytest.raises asserts that the timeout happens
            asyncio.run(
                asyncio.wait_for(                                                            # await lets the async code (like FastAPI endpoints) pause/resume while the blocking function runs in another thread.
                    asyncio.to_thread(fa.qa_chain, {"query": "What is AI?"}),                # qa_chain is synchronous: it runs from start to finish and cannot be paused/resumed, asyncio.to_thread(qa_chain, args) wraps it in a thread, returning an awaitable coroutine.
                    timeout=1                                                                # short timeout for test speed, the principle is the same: the function takes longer than the timeout → exception occurs.
                )
            )
    finally:
        fa.qa_chain = original_qa_chain
