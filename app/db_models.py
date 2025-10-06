# app/db_models.py
# Schema + DB connection setup.
# Engine = Connection factory (manages DB connections). Without engine: session doesn’t know what DB to talk to.
# Session = Workspace for making queries and commits. Without session: you can’t insert/query.
# This needs the connection URL from config, because that tells SQLAlchemy where to create the table (local Docker Postgres or cloud Supabase).

from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from app.settings import settings

Base = declarative_base()                                                        # Base class (parent that makes each class mappable to a table) for all DB models such as User, Document both inherit from the same Base.

class Document(Base):                                                            # Defines a table schema in Postgres i.e., documents table with columns (id, filename, upload_time) i.e., metadata (like a tracker/log of uploaded PDFs).
    __tablename__ = "documents"                                                 
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True)
    upload_time = Column(DateTime, default=datetime.utcnow)

# Create DB engine + session 
# Analogy: Engine = Power plug (connects to electricity source = DB), Session = Device you plug in (actually performs work).
engine = create_engine(settings.postgres_url)                                    # Creates a DB connection engine using the connection string from config.yaml. Similar to connection pool or gateway to the actual Postgres database. Without the engine, SQLAlchemy doesn’t know where the database lives.
SessionLocal = sessionmaker(bind=engine)                                         # Factory for DB sessions (so you can insert/query rows). A session is a short-lived object that is used to insert rows, query rows, commit or rollback transactions

# Initialize tables
Base.metadata.create_all(bind=engine)                                            # Actually creates the table in Postgres if it doesn’t exist. It looks at all models that inherit from Base (Document, User, etc.) and issues the necessary CREATE TABLE SQL commands.

# Example for empty table schema inside Postgres
# CREATE TABLE IF NOT EXISTS documents (
#    id SERIAL PRIMARY KEY,
#    filename VARCHAR NOT NULL UNIQUE,
#    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#);
