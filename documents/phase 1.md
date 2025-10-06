# Postgres Check, GitHub Actions, Deployment Target

## Step 1
- Update `/upload_query` endpoint to insert into Postgres when a new PDF is uploaded.
- Write a small test in `test_db.py` that simulates this.

## Step 2
- Add GitHub Actions workflow → make sure tests run automatically.
- This is super lightweight.

## Step 3
- Pick a deployment target (Render, Cloud Run, or a cheap VM).
- Deploy with docker-compose up so Postgres + FastAPI run together in the cloud.
