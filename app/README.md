# app/

## Config & Settings

- `config.yaml` (repo root) → Central configuration file for models, directories, and database.
  Example:
  ```yaml
  llm_model: "google/flan-t5-base"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  data_dir: "data"
  db_dir: "db"
  postgres_url: "postgresql://raguser:ragpass@postgres:5432/ragdb"
  default_pdf_name: "RAG_Paper.pdf"

- `settings.py` (inside app/) → Pydantic BaseSettings class that loads/validates config. Access anywhere in code with:
  ``` bash
  from app.settings import settings
  print(settings.data_dir)
  ```
## Scripts Overview

- `loader.py` → Loads PDFs, chunks text, filters out irrelevant sections.
- `embeddings.py` → Creates or loads persisted vectorstores (Chroma + embeddings) i.e., **Production tweak #1**.
- `llm.py` → Loads the language model, with quantization (int8 & compile) optimizations + batch inference + fallback strategy i.e., **Production tweak #2, #3, #4**.
- `chain.py` → Builds the QA chain (Retriever + LLM + optional metadata filtering + guardrails via prompt instructions) i.e., **Production tweak #5, #6**.
- `fastapi_app.py` → FastAPI server exposing API endpoints with model caching + timeouts i.e., **Production tweak #7, #8**:
  - `/query` → Ask questions against existing vectorstore with timeout.
  - `/upload_query` → Upload a new PDF + immediately query it with timeout.
  - `/health` → Service availability + DB status check.
 - `db_models.py` → **Flow: What happens when a PDF is uploaded?**
   - User uploads PDF → handled in FastAPI.
   - You explicitly call session.add(Document(filename="myfile.pdf")).
   - That creates a new row in documents table:

| id | filename   | upload_time         |
| -- | ---------- | ------------------- |
| 1  | report.pdf | 2025-10-04 16:30:00 |
| 2  | notes.pdf  | 2025-10-04 16:32:10 |

## Tests (Located in app/tests/)

- `test_api.py`
  - `test_pipeline` → Unit/integration test for loader → embeddings → LLM → QA chain.
  - `test_query_endpoint` → API test for /query.
  - `test_query_timeout` → Ensures queries timeout after 30s (robustness check).
  - `test_health` → API test for /health.
  - `test_upload_query` → Simulate uploading a PDF + question to /upload_query.
  - `test_settings_load` → Verifies config.yaml → settings.py integration.
- `test_db.py` → To confirm Postgres connection works inside docker-compose
