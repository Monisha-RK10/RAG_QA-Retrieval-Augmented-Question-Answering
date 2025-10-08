# app/tests/test_api.py
import asyncio
import pytest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from pathlib import Path
from unittest.mock import patch

from app.fastapi_app import app, DATA_DIR, DB_DIR, vectordb, qa_chain
from app.settings import settings

client = TestClient(app)

# -----------------------------
# Test /health endpoint
# -----------------------------
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

