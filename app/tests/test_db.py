# app/tests/test_db.py
# This test ensures:
  # The SQLAlchemy schema (Document table) is valid
  # The DB connection and session flow work (insert → commit → read)
  # It works both locally (Postgres) and in CI/CD (SQLite)
# This test doesn’t test your API, but it tests the foundation under the API (the ability to connect to the database, create tables, insert, query, and close safely.)

import os
os.environ["TEST_DATABASE_URL"] = "sqlite:///:memory:"                         # Must be set BEFORE importing db_models, “inject” a fake DB URL creates a temporary, in-memory SQLite database (no file written).

# Note: 
# Normal app run: No TEST_DATABASE_URL set → uses Postgres from settings i.e., DB engine points to the Postgres container (hostname postgres). This works only inside Docker where that hostname is valid
# Running tests: Set TEST_DATABASE_URL first → db_models reads that instead → uses SQLite i.e., overrides the default Postgres connection only during testing. Postgres only works when run via Docker Compose.

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db_models import Base, Document

# Use the env var
DB_URL = os.environ.get("TEST_DATABASE_URL")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})
SessionLocal = sessionmaker(bind=engine)

# Create tables for the test
Base.metadata.create_all(bind=engine)                                                 # Since SQLite :memory:, this means: Create the schema fresh in memory for each test run. In production, Postgres already has these tables from migrations, so this is just a local safety step.

@pytest.mark.integration
def test_db_insert():
    """
    Insert a Document row and read it back.
    Works for SQLite in-memory or a real Postgres DB.
    """
    session = SessionLocal()
    try:
        doc = Document(filename="test.pdf")
        session.add(doc)
        session.commit()                                                              # Actually writes it to the DB.

        saved = session.query(Document).filter_by(filename="test.pdf").first()        # Runs a SELECT query on the Document table to retrieve the record that was just inserted.
        assert saved is not None, "Document not saved to DB"                          # Two basic checks: Did the object save correctly? Did we retrieve the same filename?
        assert saved.filename == "test.pdf", "Filename mismatch"
    finally:
        session.close()
