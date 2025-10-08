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
from app.db_models import SessionLocal

# app/fastapi_app.py
from fastapi import FastAPI

app = FastAPI(title="RAG API")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
