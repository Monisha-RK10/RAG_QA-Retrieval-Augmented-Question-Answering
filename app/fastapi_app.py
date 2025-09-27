# app/fastapi_app.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from pydantic import BaseModel

from app.loader import load_and_chunk_pdf
from app.embeddings import load_or_create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# --------------------------
# Config & Directories
# --------------------------
DATA_DIR = Path("data")
DB_DIR = Path("db")
DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# --------------------------
# FastAPI App
# --------------------------
app = FastAPI(title="RAG API")

# --------------------------
# Load LLM once at startup
# --------------------------
llm = load_llm()

# --------------------------
# Load persisted vectorstore or create from default PDF
# --------------------------
default_pdf = DATA_DIR / "RAG_Paper.pdf"
if DB_DIR.exists() and any(DB_DIR.iterdir()):
    vectordb = Chroma(
        persist_directory=str(DB_DIR),
        embedding_function=embeddings
    )
elif default_pdf.exists():
    chunks = load_and_chunk_pdf(str(default_pdf))
    vectordb = load_or_create_vectorstore(chunks, persist_directory=str(DB_DIR))
else:
    vectordb = None


# --------------------------
# Build QA chain if vectordb exists
# --------------------------
qa_chain = build_qa_chain(llm, vectordb) if vectordb else None

# --------------------------
# Pydantic Model for Query
# --------------------------
class QueryRequest(BaseModel):
    question: str

# --------------------------
# API Endpoints
# --------------------------
@app.post("/query")
async def query_document(request: QueryRequest):
    """
    Run a question against the persisted vectorstore.
    """
    if not vectordb or not qa_chain:
        raise HTTPException(
            status_code=400, 
            detail="No vectorstore found. Upload a PDF first."
        )

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
    vectordb_local = load_or_create_vectorstore(chunks, persist_directory=str(DB_DIR))

    # Build QA chain for this PDF
    qa_chain_local = build_qa_chain(llm, vectordb_local)

    # Run query
    result = qa_chain_local({"query": question})
    return JSONResponse({"answer": result["result"]})
