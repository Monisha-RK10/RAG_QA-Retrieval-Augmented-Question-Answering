# app/db_models.py
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from app.settings import settings

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True)
    upload_time = Column(DateTime, default=datetime.utcnow)

# Create DB engine + session
engine = create_engine(settings.postgres_url)
SessionLocal = sessionmaker(bind=engine)

# Initialize tables
Base.metadata.create_all(bind=engine)
