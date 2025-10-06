# app/tests/test_db.py
# test_db.py is an integration test that makes sure:
  # You can open a DB session (SessionLocal()).
  # Insert a Document row.
  # Commit and retrieve it back.
  # Assert it worked.
# So test_db.py verifies the schema + connection actually work

from app.db_models import SessionLocal, Document

def test_db_insert():
    session = SessionLocal()
    doc = Document(filename="test.pdf")
    session.add(doc)
    session.commit()

    saved = session.query(Document).filter_by(filename="test.pdf").first()
    assert saved is not None
    session.close()
