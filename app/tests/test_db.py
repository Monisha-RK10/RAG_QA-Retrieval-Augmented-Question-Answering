# app/tests/test_db.py
# test_db.py is an integration test that makes sure:
  # You can open a DB session (SessionLocal()).
  # Insert a Document row.
  # Commit and retrieve it back.
  # Assert it worked.
# So test_db.py verifies the schema + connection actually work

# Note: test_db.py proves Postgres works in isolation. But in production, you want real app behavior.
# fastapi_app.py is where we connect Postgres to the actual workflow i.e., When a user uploads a PDF → not only save file + embed → but also insert metadata row (filename, upload_time) into Postgres.
# Without this, Postgres never gets used in the live pipeline (only in tests).

from app.db_models import SessionLocal, Document

def test_db_insert():
    session = SessionLocal()
    doc = Document(filename="test.pdf")
    session.add(doc)
    session.commit()

    saved = session.query(Document).filter_by(filename="test.pdf").first()
    assert saved is not None
    session.close()
