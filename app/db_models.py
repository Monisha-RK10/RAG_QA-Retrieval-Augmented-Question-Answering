# app/db_models.py
# Defines tables (Document), engine (engine = create_engine(...)) and session (SessionLocal). Production code uses settings.postgres_url.

import os

if os.getenv("SKIP_DB_INIT", "false").lower() == "true":
    engine = None
    SessionLocal = None
    Base = None
else:
    # existing DB setup
    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import Column, Integer, String, DateTime, create_engine
    from sqlalchemy.orm import declarative_base, sessionmaker
    from datetime import datetime
    from app.settings import settings
    import os

    class Document(Base):
        __tablename__ = "documents"
        id = Column(Integer, primary_key=True, index=True)
        filename = Column(String, unique=True)
        upload_time = Column(DateTime, default=datetime.utcnow)

    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    Base.metadata.create_all(bind=engine)
