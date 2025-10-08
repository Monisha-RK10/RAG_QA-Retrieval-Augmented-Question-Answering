# app/fastapi_app.py
import asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.loader import load_and_chunk_pdf
from app.embeddings import load_or_create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.settings import settings

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

    pdf_path = DATA_DIR / file.filename
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

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
