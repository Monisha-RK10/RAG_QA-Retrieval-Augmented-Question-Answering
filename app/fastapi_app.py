# app/fastapi_app.py
# main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from app.loader import load_and_chunk_pdf
from app.embeddings import create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from langchain_community.vectorstores import Chroma
from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str

from fastapi import HTTPException

# Load or create vectorstore at startup
chunks = load_and_chunk_pdf("data/RAG_Paper.pdf")
vectordb = create_vectorstore(chunks, persist_directory="db")
llm = load_llm()
qa_chain = build_qa_chain(llm, vectordb)

app = FastAPI(title="RAG API")

DATA_DIR = Path("data")
DB_DIR = Path("db")
DB_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Load LLM once at startup
llm = load_llm()

# Load existing persisted vectorstore if available
if DB_DIR.exists() and any(DB_DIR.iterdir()):
    vectordb = Chroma(persist_directory=str(DB_DIR))
else:
    vectordb = None  # Will create dynamically if a PDF is uploaded

# Build QA chain if vectordb exists
qa_chain = build_qa_chain(llm, vectordb) if vectordb else None


@app.post("/query")
async def query_document(request: QueryRequest):
    """
    Run a question against the persisted vectorstore.
    """
    if not vectordb:
        raise HTTPException(status_code=400, detail="No vectorstore found. Upload a PDF first.")

    result = qa_chain({"query": request.question})
    return {"answer": result["result"]}


@app.post("/upload_query")
async def upload_query(file: UploadFile = File(...), question: str = ""):
    """
    Upload a PDF, embed it, and immediately run a query.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save uploaded PDF to data/
    pdf_path = DATA_DIR / file.filename
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    # Load & chunk PDF
    chunks = load_and_chunk_pdf(str(pdf_path))

    if not chunks:
        raise HTTPException(status_code=400, detail="PDF has no valid content to embed.")

    # Create vectorstore and persist
    vectordb_local = create_vectorstore(chunks, persist_directory=str(DB_DIR))

    # Build QA chain for this PDF
    qa_chain_local = build_qa_chain(llm, vectordb_local)

    # Run query
    result = qa_chain_local({"query": question})
    return JSONResponse({"answer": result["result"]})
