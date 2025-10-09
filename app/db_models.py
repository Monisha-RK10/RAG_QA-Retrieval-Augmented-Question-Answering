# app/db_models.py
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

# Use TEST_DATABASE_URL if set (CI / tests), else default Postgres
DB_URL = os.environ.get("TEST_DATABASE_URL", settings.postgres_url)

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})
SessionLocal = sessionmaker(bind=engine)

# Only create tables if DB_URL is not empty
Base.metadata.create_all(bind=engine)
