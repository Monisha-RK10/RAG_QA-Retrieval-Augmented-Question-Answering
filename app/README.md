# app/

## Scripts Overview

- `loader.py` → Loads PDFs, chunks text, filters out irrelevant sections.
- `embeddings.py` → Creates or loads persisted vectorstores (Chroma + embeddings).
- `llm.py` → Loads the language model, with caching + quantization optimizations.
- `chain.py` → Builds the QA chain (Retriever + LLM + optional metadata filtering).
- `fastapi_app.py` → FastAPI server exposing API endpoints:
  - `/query` → Ask questions against existing vectorstore with timeout.
  - `/upload_query` → Upload a new PDF + immediately query it with timeout.
  - `/health` → Service availability + DB status check.
 
## Tests (Located in app/tests/test_api.py)

- `test_pipeline` → Unit/integration test for loader → embeddings → LLM → QA chain.
- `test_query_endpoint` → API test for /query.
- `test_query_timeout` → Ensures queries timeout after 30s (robustness check).
- `test_health` → API test for /health.
- (coming next) `test_upload_query` → Simulate uploading a PDF + question to /upload_query.
