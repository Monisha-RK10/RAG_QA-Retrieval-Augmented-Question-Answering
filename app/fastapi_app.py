# app/fastapi_app.py
# Production tweak #7: Model caching at startup, load LLM once at startup (FastAPI app startup).
# Production tweak #8: Timeouts for query endpoints.

# app/fastapi_app.py
from fastapi import FastAPI

app = FastAPI(title="RAG API")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
