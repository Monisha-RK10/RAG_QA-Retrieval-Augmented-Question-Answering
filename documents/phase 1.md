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

### Step 1: Input + Output for Postgres Check
**Input**
- Created the `documents` table in **Supabase via SQL editor**.
- Successfully inserted + queried rows via the **Supabase Python client**.

```
create table documents (
    id serial primary key,
    filename text unique,
    upload_time timestamp default now()
);
```
**Output**
```
Insert response: data=[{'id': 1, 'filename': '/content/RAG_QA/data/RAG_Paper.pdf', 'upload_time': '2025-10-07T22:55:50.521976'}] count=None
All rows: [{'id': 1, 'filename': '/content/RAG_QA/data/RAG_Paper.pdf', 'upload_time': '2025-10-07T22:55:50.521976'}]
```
**Note:** This proves the Postgres DB is live and reachable, just not over raw TCP currently. 

---
### Step 2: GitHub Actions
- Add GitHub Actions workflow → make sure tests run automatically.
  
| Stage                    | Trigger                       | Runs        | Description |
| ------------------------ | ----------------------------- | ----------- | ------------|
| **Unit & Lint (CI)**     | every push/PR                 |  automatic | `/health`(model+db), settings sanity|
| **Integration (Manual)** | “Run workflow” in Actions tab |  manual| `/query`(RAG mocked or real), internal RAG logic, internal asyn timeout, `/upload_query` timeout, db connection |

---
### Step 3: Deployment Target

**Goal:** Deploy FastAPI + RAG API to a live cloud environment with Postgres connectivity, accessible via public endpoint.

- Pick a deployment target (Render, Cloud Run, or a cheap VM).
- Deploy with docker-compose up so Postgres + FastAPI run together in the cloud.

**Deployment Steps**

- **Provision a Cloud VM (AWS EC2)**
  - Created a t2.medium Ubuntu 22.04 instance on AWS EC2.
  - Configured Security Groups to open:
    - `22` → SSH (restricted to my IP)
    - `8000 `→ FastAPI HTTP traffic
    - `5432` → Postgres (only for internal or trusted IPs)
  - Verified inbound/outbound rules via AWS Console → Network → Security Groups.
- **SSH Setup and Deployment**
  - FastAPI container served at 0.0.0.0:8000.
  - Connected to cloud Postgres via connection string in config.yaml.
```bash
ssh -i "rag_server.pem" ubuntu@<EC2_PUBLIC_IP>
git clone https://github.com/monisha-ai/RAG_QA.git
cd RAG_QA
docker compose up --build -d
```
- **Reverse Proxy (Optional)**
  - Use Nginx to route incoming requests on port 80 → FastAPI :8000.
  - Configure simple systemd service for auto-restart.
- **Validation**
```bash
curl http://51.21.196.36:8000/health
→ {"status":"ok","db":"connected"}
```
- **API Docs**

Swagger UI available at →
🔗 [http://51.21.196.36:8000/docs](http://51.21.196.36:8000/docs)

### Swagger UI (Try the API interactively):
![Swagger UI Screenshot](https://github.com/Monisha-RK10//RAG_QA-Retrieval-Augmented-Question-Answering/blob/main/output/swagger_ui.png?raw=true)

### Sample Prediction (Query)
![Prediction result](https://github.com/Monisha-RK10//RAG_QA-Retrieval-Augmented-Question-Answering/blob/main/output/output_predict.png?raw=true)
