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
DATA_DIR = Path(settings.data_dir)
DB_DIR = Path(settings.db_dir)
DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

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
    llm = load_llm()

    default_pdf = DATA_DIR / settings.default_pdf_name

    if DB_DIR.exists() and any(DB_DIR.iterdir()):
        vectordb = Chroma(persist_directory=str(DB_DIR), embedding_function=embeddings)
    elif default_pdf.exists():
        chunks = load_and_chunk_pdf(str(default_pdf))
        vectordb = load_or_create_vectorstore(chunks, persist_directory=str(DB_DIR))
    else:
        vectordb = None

    if vectordb:
        qa_chain = build_qa_chain(llm, vectordb)

# --------------------------
# Endpoints
# --------------------------
@app.get("/health")
async def health_check():
    return {"status": "ok"}
