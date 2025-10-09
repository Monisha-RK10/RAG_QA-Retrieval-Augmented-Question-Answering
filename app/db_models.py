# app/db_models.py
# Defines tables (Document), engine (create_engine(...)) and session (SessionLocal).

from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from app.settings import settings
import os

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True)
    upload_time = Column(DateTime, default=datetime.utcnow)


# --------------------------------------------------------
# Safe DB initialization (CI/CD-friendly)
# --------------------------------------------------------

# Allow skipping DB during tests or CI (avoids psycopg2 errors)
if os.getenv("SKIP_DB_INIT", "false").lower() == "true":
    engine = None
    SessionLocal = None
else:
    # Use TEST_DATABASE_URL if set (e.g., SQLite), else fallback to Postgres
    DB_URL = os.environ.get("TEST_DATABASE_URL", settings.postgres_url)

    engine = create_engine(
        DB_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {}
    )
    SessionLocal = sessionmaker(bind=engine)

    # Create tables only if engine is valid
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[Warning] Could not create tables: {e}")
        SessionLocal = None
