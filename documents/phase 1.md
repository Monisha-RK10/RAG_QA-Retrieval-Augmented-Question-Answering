# Phase 1: Deploy Basic Infra
## Postgres Check, GitHub Actions, Deployment Target

### Step 1: Postgres Check
- Update `/upload_query` endpoint to insert into Postgres when a new PDF is uploaded.
- Write a small test in `test_db.py` that simulates this.

```bash
- Sign up for a free cloud Postgres
- Update the `config.yaml` (where the Postgres connection string lives, you will get this info from cloud Postgres)
- Modify `db_models.py` (the simplest way to check if the Postgres connection is alive)
- Run the test (`test_db.py`) [pytest app/tests/test_db.py -v]
- Extend `fastapi_app.py` upload flow (add code to insert metadata row into Postgres on upload.)
```

**Note:**
- Docker Compose is useful when everything is run together on the local machine or cloud (FastAPI + Postgres as services).
- So for now → I use cloud Postgres.
- Docker Compose will come back when I deploy (later in Phase 1).
- Also, Postgres does not participate in embeddings or retrieval. That part is still handled by Chroma.
- Postgres stores metadata
  - `file_id`, `filename`, `uploaded_by`, `upload_time`, `num_chunks`
  - Maybe status flags (`processed = True/False`)
  - Deleting or fetching PDF info.
- So:
  - Postgres = “library catalog” (tracks which PDFs exist, when, who uploaded).
  - Chroma = “knowledge inside the books” (stores embeddings of actual text).

### Step 2: GitHub Actions
- Add GitHub Actions workflow → make sure tests run automatically.
- This is super lightweight.

### Step 3: Deployment Target
- Pick a deployment target (Render, Cloud Run, or a cheap VM).
- Deploy with docker-compose up so Postgres + FastAPI run together in the cloud.
