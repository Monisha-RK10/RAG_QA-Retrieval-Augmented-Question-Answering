# app/fastapi_app.py
from fastapi import FastAPI

app = FastAPI(title="RAG API")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
