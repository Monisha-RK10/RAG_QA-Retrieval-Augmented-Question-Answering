from fastapi.testclient import TestClient
from app.fastapi_app import app
from app.loader import load_and_chunk_pdf
from app.embeddings import load_or_create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from langchain_community.vectorstores import Chroma

client = TestClient(app)

# Test the loader + embeddings + chain
def test_pipeline():
    # 1. Load PDF
    chunks = load_and_chunk_pdf("data/RAG_Paper.pdf")
    assert len(chunks) > 0, "No chunks loaded"

    # 2. Create vectorstore
    vectordb = create_vectorstore(chunks, persist_directory="db")
    assert vectordb is not None, "Vectorstore creation failed"

    # 3. Load LLM
    llm = load_llm()
    assert llm is not None, "LLM load failed"

    # 4. Build QA chain
    qa_chain = build_qa_chain(llm, vectordb)
    result = qa_chain({"query": "What is Abstractive Question Answering"})
    print("Test query answer:", result["result"])
   # assert "Abstractive" in result["result"].lower(), "Unexpected answer"
    assert result["result"], "QA chain returned empty answer"


# Test FastAPI /query endpoint
def test_query_endpoint():
    response = client.post("/query", json={"question": "What is Abstractive Question Answering?"})
    #print("API response:", response.json())
    assert response.status_code == 200
    print(response.json())
