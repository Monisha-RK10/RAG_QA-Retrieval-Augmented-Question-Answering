# Phase 1: Deploy Basic Infra
## Postgres Check, GitHub Actions, Deployment Target

### Step 1: Postgres Check
- Update `/upload_query` endpoint to insert into Postgres when a new PDF is uploaded.
- Write a small test in `test_db.py` that simulates this.

```bash
- Sign up for a free cloud Postgres
- Update the `config.yaml`
- Modify `db_models.py`
- Run the test (`test_db.py`)
- Extend `fastapi_app.py` upload flow
```

### Step 2: GitHub Actions
- Add GitHub Actions workflow → make sure tests run automatically.
- This is super lightweight.

### Step 3: Deployment Target
- Pick a deployment target (Render, Cloud Run, or a cheap VM).
- Deploy with docker-compose up so Postgres + FastAPI run together in the cloud.
