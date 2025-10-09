# app/

## Config & Settings

- `config.yaml` (repo root) → Central configuration file for models, directories, and database.
- `settings.py` (inside app/) → Pydantic BaseSettings class that loads/validates config. Access anywhere in code with:

## Scripts Overview

- `loader.py` → Loads PDFs, chunks text, filters out irrelevant sections.
- `embeddings.py` → Creates or loads persisted vectorstores (Chroma + embeddings) i.e., **Production tweak #1**.
- `llm.py` → Loads the language model, with quantization (int8 & compile) optimizations + batch inference + fallback strategy i.e., **Production tweak #2, #3, #4**.
- `chain.py` → Builds the QA chain (Retriever + LLM + optional metadata filtering + guardrails via prompt instructions) i.e., **Production tweak #5, #6**.
- `fastapi_app.py` → FastAPI server exposing API endpoints with model caching + timeouts i.e., **Production tweak #7, #8**:
  - `/health` → Lightweight (service model + db )check
  - `/query` → Query existing RAG pipeline (cached vectorstore + LLM) with timeout
  - `/upload_query` → Upload PDF + embed + query immediately with timeout
 - `db_models.py`  →
   - **Flow:** What happens when a PDF is uploaded?
   - **Supports:** SQLite (CI test) and Postgres (Docker)
   - User uploads PDF (handled in FastAPI) → explicitly call session.add(Document(filename="myfile.pdf"))  → That creates a new row in documents table:
| id | filename   | upload_time         |
| -- | ---------- | ------------------- |
| 1  | report.pdf | 2025-10-04 16:30:00 |
| 2  | notes.pdf  | 2025-10-04 16:32:10 |


## Tests (Located in app/tests/)

- `test_api.py` 
  - **Purpose:** Fast checks to catch obvious regressions before merge.
  - **Light tests, run on every push/PR**
    - `test_health` → verifies API is alive.
    - `test_settings_load` → ensures environment/config parsing works.
- `test_integration.py` 
  - **Purpose:** Full end-to-end correctness and robustness checks.
  - **Heavy tests, manual trigger only, triggered by `workflow_dispatch` in GitHub Actions**
    - `test_full_rag_pipeline` → PDF → chunks → vector DB → LLM → answer pipeline works end-to-end.
    - `test_qa_chain_timeout` → validates timeout handling in the async wrapper.
    - `test_upload_query_timeout` → validates the new /upload_query endpoint: upload + embed + query with enforced timeout.
    - `test_query_endpoint` → minimal integration check that your /query endpoint runs and returns a response.  
- `test_db.py` 
  - **Purpose:** To confirm if Postgres connection works
  - **Works both locally (Postgres) and in CI/CD (SQLite)**
