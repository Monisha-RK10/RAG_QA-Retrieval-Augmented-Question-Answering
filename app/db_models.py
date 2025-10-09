# app/db_models.py
# Defines tables ORM model (Document), SQLAlchemy engine (connection to DB, create_engine(...)) and SessionLocal (session factory for DB queries).

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
if os.getenv("SKIP_DB_INIT", "false").lower() == "true":                                   # SKIP_DB_INIT=false (default)
    engine = None                                                                          # The connection pool to the database. Knows how to talk SQL.
    SessionLocal = None                                                                    # A factory that creates DB sessions (each one representing a short-lived DB transaction).
else:
    # Use TEST_DATABASE_URL if set (e.g., SQLite), else fallback to Postgres
    DB_URL = os.environ.get("TEST_DATABASE_URL", settings.postgres_url)

    engine = create_engine(
        DB_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {}            # "check_same_thread": False for sqlite, multiple threads reuse the same SQLite connection safely in a testing context.
    )
    SessionLocal = sessionmaker(bind=engine)

    # Create tables only if engine is valid
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:                                                                 # If SKIP_DB_INIT=true, engine and SessionLocal are None-> TypeError, In /health endpoint, this is handled carefullyi.e., try/except will catch the error and respond '{"status": "fail", "db_error": "'NoneType' object is not callable"}'-> 1) API doesn’t crash 2) CI stays green even with no DB.
        print(f"[Warning] Could not create tables: {e}")
        SessionLocal = None
