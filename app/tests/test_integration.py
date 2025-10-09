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
