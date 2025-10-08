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


@app.get("/health")
async def health_check():
    return {"status": "ok"}
