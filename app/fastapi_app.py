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

@app.post("/query")
async def query_document(request: QueryRequest):
    if not vectordb or not qa_chain:
        raise HTTPException(status_code=400, detail="No vectorstore found. Upload a PDF first.")

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(qa_chain, {"query": request.question}),
            timeout=30
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Query timed out after 30s")

    return {"answer": result["result"]}

@app.post("/upload_query")
async def upload_query(file: UploadFile = File(...), question: str = ""):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save uploaded PDF to DATA_DIR
    DATA_DIR.mkdir(exist_ok=True)
    pdf_path = DATA_DIR / file.filename
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    # Only attempt chunking if file exists
    if not pdf_path.exists():
        raise HTTPException(status_code=500, detail="PDF save failed.")

    chunks = load_and_chunk_pdf(str(pdf_path))
    if not chunks:
        raise HTTPException(status_code=400, detail="PDF has no valid content to embed.")

    vectordb_local = load_or_create_vectorstore(chunks, persist_directory=str(DB_DIR))
    qa_chain_local = build_qa_chain(llm, vectordb_local)

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(qa_chain_local, {"query": question}),
            timeout=30
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Query timed out after 30s")

    return JSONResponse({"answer": result["result"]})
