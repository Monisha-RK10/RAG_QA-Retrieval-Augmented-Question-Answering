# app/tests/test_db.py
from app.db_models import SessionLocal, Document

def test_db_insert():
    session = SessionLocal()
    doc = Document(filename="test.pdf")
    session.add(doc)
    session.commit()

    saved = session.query(Document).filter_by(filename="test.pdf").first()
    assert saved is not None
    session.close()
