# Phase 0 — Productionize the Repo

- Dockerize FastAPI (Dockerfile). Add `docker-compose.yml` for local dev.
- Add `config.yaml` / env support, Pydantic settings.
- Add simple Postgres (local via Docker) to save metadata.

### 1. Why Dockerize FastAPI?
To make your app portable, reproducible. For this, add 'Dockerfile'. It build image → copy code inside → when container runs, start uvicorn server.

### 2. Why add 'docker-compose.yml' for local dev?
This is required for multiple services (FastAPI, Postgres, maybe Redis).

### 3. Docker vs Docker Compose?
Docker = runs one container (e.g., your API).
docker run -p 8000:8000 rag-api → only API is up.
Docker Compose = runs multiple containers as a system.
Example: one for API, one for Postgres, one for Redis.
You define all services + their networking in one YAML file.
Then run: docker-compose up → all services spin up together.
Analogy:
Docker = you run a single program manually.
Compose = you run a whole stack with one command

### 4. What does docker compose usually contain?
services: 
Each block is a separate container.
api service = runs your FastAPI Dockerfile.
postgres service = runs official Postgres image
ports:
"8000:8000" → expose API on host port 8000.
"5432: 5432"  → expose Postgres DB on host port 5432.
 They're separate because API and DB are different processes. 
volumes:
Mounts persistent storage.
- .:/app → maps your local project folder into container /app (good for dev → live code sync).
- postgres_data:/var/lib/postgresql/data → stores DB files outside the container, so if the container restarts, data isn't lost.
That's why paths differ: API mounts code, Postgres mounts DB storage. 
"Run my FastAPI app + Postgres DB together, wire them up, give API env vars to connect to DB"

### 5. Why config via config.yaml + Pydantic Settings?
To avoid hardcoded paths/models/db URLs in code. 
config.yaml = configs in plain YAML, human-readable static config file (easy to edit, commit to git). 
Example: llm_model: "google/flan-t5-base"
embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
settings.py = Python way to read + validate that config, Python loader + validator using Pydantic. It reads config.yaml, parses it into a Settings object with correct types.
Example: settings.llm_model # str
settings.data_dir # str 
YAML → for devs to edit easily.
Pydantic → for app to safely consume config.

### 6. Benefits of Pydantic settings?
(i) Type-checked (if 'llm_model' is missing, it errors early).
(ii) Can merge with env vars (e.g., override DB password in production without touching YAML).
(iii) Avoids "magic strings" everywhere.

### 7. Why add Postgres for metadata?
Persist chunks in Chroma only is fine for small demos, but you will need structured storage too.
Why Postgres:
(i) Store file metadata (file_id, filename, uploaded_by, upload_time, num_chunks, etc).
(ii) Good for queries like: "Which PDFs were uploaded last week?" or "Delete all PDFs for user X."
(iii) Keep vector DB (Chroma, Pinecone, FAISS) separate for embeddings. Postgres is not replacing it, it complements it. 
Every time a PDF is uploaded, you would insert a row into Postgres alongside storing its embeddings in Chroma.
