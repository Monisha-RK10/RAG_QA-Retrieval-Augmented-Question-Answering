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
 - `db_models.py`  → Flow: What happens when a PDF is uploaded? 
``` bash
User uploads PDF (handled in FastAPI) → explicitly call session.add(Document(filename="myfile.pdf"))  → That creates a new row in documents table:
```
| id | filename   | upload_time         |
| -- | ---------- | ------------------- |
| 1  | report.pdf | 2025-10-04 16:30:00 |
| 2  | notes.pdf  | 2025-10-04 16:32:10 |


## Tests (Located in app/tests/)

- `test_api.py` (runs every push/PR)
  - `test_health` → API health check.
  - `test_settings_load` → Config parsing test.
  - `test_query_endpoint` → API + pipeline integration.
- `test_integration.py` (run heavy tests manually)
  - `test_full_rag_pipeline` → Real end-to-end RAG check (integration).
  - `test_qa_chain_timeout` → Time out test. 
  - `test_upload_query_timeout` → Full endpoint coverage (upload + query) with timeout logic (simulate uploading a PDF + question to /upload_query).
  
- `test_db.py` → To confirm Postgres connection works inside docker-compose
