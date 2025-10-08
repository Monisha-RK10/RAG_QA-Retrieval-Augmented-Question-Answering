# app/tests/test_api.py

import asyncio
import pytest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from pathlib import Path

from app.fastapi_app import app, DB_DIR, vectordb, qa_chain
from app.loader import load_and_chunk_pdf
from app.embeddings import load_or_create_vectorstore
from app.llm import load_llm
from app.chain import build_qa_chain
from app.settings import settings

client = TestClient(app)

# -----------------------------
# Test FastAPI /health
# -----------------------------
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

