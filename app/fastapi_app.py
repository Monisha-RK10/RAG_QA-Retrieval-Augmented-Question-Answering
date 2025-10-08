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
#from app.db_models import SessionLocal

# app/fastapi_app.py
from fastapi import FastAPI

# --------------------------
# FastAPI App
# --------------------------
app = FastAPI(title="RAG API")

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

# Globals (will be initialized in startup event)
embeddings = None
llm = None
vectordb = None
qa_chain = None

# --------------------------
# Pydantic Model
# --------------------------
class QueryRequest(BaseModel):
    question: str

# --------------------------
# Startup event (lazy initialization)
# --------------------------
@app.on_event("startup")
async def startup_event():
    global embeddings, llm, vectordb, qa_chain

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    # --------------------------
    # Load LLM once at startup
    # --------------------------
    llm = load_llm()                                                                                      # Production tweak #5: Model caching at startup, without this, every query would reload the model = huge latency hit.

    default_pdf = DATA_DIR / settings.default_pdf_name

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
# Health Check Endpoint
# --------------------------
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint for monitoring and orchestration systems.
    Returns 200 OK if the API is alive and ready.
    """
    return {"status": "ok"}

