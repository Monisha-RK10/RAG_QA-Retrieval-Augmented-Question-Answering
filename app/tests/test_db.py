# app/tests/test_db.py
# Integration test for DB connectivity and schema, switching to SQLite for CI, (to avoid the “host not found” error).
# Works in CI (SQLite) or locally (Postgres if available).

import os
os.environ["TEST_DATABASE_URL"] = "sqlite:///:memory:"  # must be set BEFORE importing db_models

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db_models import Base, Document

# Use the env var
DB_URL = os.environ.get("TEST_DATABASE_URL")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})
SessionLocal = sessionmaker(bind=engine)

# Create tables for the test
Base.metadata.create_all(bind=engine)

@pytest.mark.integration_manual  # mark as manual integration test
def test_db_insert():
    """
    Insert a Document row and read it back.
    Works for SQLite in-memory or a real Postgres DB.
    """
    session = SessionLocal()
    try:
        doc = Document(filename="test.pdf")
        session.add(doc)
        session.commit()

        saved = session.query(Document).filter_by(filename="test.pdf").first()
        assert saved is not None, "Document not saved to DB"
        assert saved.filename == "test.pdf", "Filename mismatch"
    finally:
        session.close()
