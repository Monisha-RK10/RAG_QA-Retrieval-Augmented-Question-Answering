# app/fastapi_app.py
# Production tweak #7: Model caching at startup, load LLM once at startup (FastAPI app startup).
# Production tweak #8: Timeouts for query endpoints.

import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException                                          # Import framework to serve RAG system as an HTTP API, upload files (PDFs), clean error responses
from fastapi.responses import JSONResponse                                                            # Consistent JSON replies.
from pathlib import Path
from pydantic import BaseModel                                                                        # Pydantic model for request validation.

from app.loader import load_and_chunk_pdf                                                             # Modular pieces of code
from app.embeddings import load_or_create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.settings import settings

# --------------------------
# Config & Directories
# --------------------------
#DATA_DIR = Path("data")                                                                               # Ensures data/ for PDFs and db/ for vector DB exist.
#DB_DIR = Path("db")

DATA_DIR = Path(settings.data_dir)
DB_DIR = Path(settings.db_dir)
DATA_DIR.mkdir(exist_ok=True)                                                                         # Avoids crash if directories already exist
DB_DIR.mkdir(exist_ok=True)

#EMBEDDING_MODEL = "all-MiniLM-L6-v2"                                                                  # Picking a small, fast embedding model.
EMBEDDING_MODEL = settings.embedding_model
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)                                        # embeddings object gets reused everywhere → avoids repeated initialization.

# --------------------------
# FastAPI App
# --------------------------
app = FastAPI(title="RAG API")                                                                        # Defines the API server, with docs automatically generated at /docs

# --------------------------
# Load LLM once at startup
# --------------------------
llm = load_llm()                                                                                      # Production tweak #5: Model caching at startup, without this, every query would reload the model = huge latency hit.

# --------------------------
# Load persisted vectorstore or create from default PDF
# --------------------------
default_pdf = DATA_DIR / "RAG_Paper.pdf"
if DB_DIR.exists() and any(DB_DIR.iterdir()):                                                         # Checks 3 cases: If a persisted DB exists → reload it (fast startup), Else if a default PDF exists → create a new DB, Else → no DB (wait for upload). This is smart fallback design (Production tweak #4).                                                      
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
qa_chain = build_qa_chain(llm, vectordb) if vectordb else None                                        # Builds the LangChain chain (LLM + retriever), only initializes if a DB is present.

# --------------------------
# Pydantic Model for Query
# --------------------------
class QueryRequest(BaseModel):                                                                        # Enforces input validation → if user sends bad JSON, FastAPI rejects it automatically.
    question: str

# --------------------------
# API Endpoints
# --------------------------
@app.post("/query")
async def query_document(request: QueryRequest):                                                      # Test 1: /query with a known PDF, For questions on the already-loaded or persisted knowledge base. Example: The system already has RAG_Paper.pdf embedded. User just asks: “What are the limitations?”, Faster → no upload step.
    """
    Run a question against the persisted vectorstore with timeout.
    """
    if not vectordb or not qa_chain:
        raise HTTPException(
            status_code=400, 
            detail="No vectorstore found. Upload a PDF first."
        )

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(qa_chain, {"query": request.question}),
            timeout=30
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Query timed out after 30s")

    return {"answer": result["result"]}

@app.post("/upload_query")                                                                            # Test 2: /upload_query with an uploaded PDF, For ad-hoc queries on a new document. Example: User uploads “invoice.pdf” and immediately asks: “What’s the total amount due?” This workflow combines upload + embedding + query into one request.
async def upload_query(file: UploadFile = File(...), question: str = ""):
    """
    Upload a PDF, embed it, and immediately run a query with timeout.
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

    try:
        result = await asyncio.wait_for(                                                              # Enforces timeout.
            asyncio.to_thread(qa_chain_local, {"query": question}),                                   # Runs blocking code in a separate thread.
            timeout=30
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Query timed out after 30s")

    return JSONResponse({"answer": result["result"]})

# --------------------------
# Health Check Endpoint
# --------------------------
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint for monitoring and orchestration systems.
    Returns 200 OK if the API is alive and ready.
    """
    return {"status": "ok"}
