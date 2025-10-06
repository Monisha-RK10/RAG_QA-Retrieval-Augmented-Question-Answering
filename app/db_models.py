# app/db_models.py
# Schema + DB connection setup.
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from app.settings import settings

Base = declarative_base()                                                        # Base class for all DB models.

class Document(Base):                                                            # Defines a documents table with columns (id, filename, upload_time).
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True)
    upload_time = Column(DateTime, default=datetime.utcnow)

# Create DB engine + session
engine = create_engine(settings.postgres_url)                                    # Creates a DB connection engine using the connection string from config.yaml.
SessionLocal = sessionmaker(bind=engine)                                         # Factory for DB sessions (so you can insert/query rows).

# Initialize tables
Base.metadata.create_all(bind=engine)                                            # Actually creates the table in Postgres if it doesn’t exist.
