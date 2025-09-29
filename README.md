# Retrieval-Augmented Generation (RAG) QA System

This project implements a Retrieval-Augmented Generation (RAG) pipeline for question answering over PDFs.
It combines vector search + large language models and serves results via a FastAPI backend.

Blog post (concept + pipeline walkthrough):

[RAG Pipeline for Travel Data](https://medium.com/@monishatemp20/rag-2-rag-pipeline-for-travel-data-part-1-41abe0fea2b1)

## Pipeline Overview

- Loader → Parse & chunk PDFs into text passages.
- Embeddings + Vector DB → Encode passages, persist them in Chroma.
- Retriever → Retrieve top-k relevant chunks per query.
- LLM → Answer using retrieved context (Flan-T5, quantized for efficiency).
- FastAPI Server → Expose /query, /upload_query, /health endpoints.

## Project Structure

RAG_QA/
│── app/
│   ├── loader.py        # PDF loading + chunking
│   ├── embeddings.py    # Embeddings + Chroma vectorstore
│   ├── llm.py           # LLM loading + quantization
│   ├── chain.py         # RAG pipeline (retriever + LLM chain)
│   ├── fastapi_app.py   # API endpoints
│   └── tests/
│       └── test_api.py  # Unit + integration tests
│
│── documents/           # Example PDFs
│── db/                  # Persisted vectorstore
│── data/                # Temp data / scratch
│── requirements.txt
│── README.md (this file)


## Production Tweaks Implemented

- Vector DB Caching → Persist embeddings once, reuse later.
- Quantization + Torch Compile → Faster inference, lower memory.
- Batch Inference → Process multiple queries in parallel.
- Fallback Models → Graceful degradation if GPU unavailable.
- Metadata Filtering → Restrict retrieval by document metadata.
- Prompt Guardrails → Style/content control, safe fallback answers.
- Model Caching at Startup → No repeated heavy init per request.
- Timeouts → Prevent hanging requests.
  
## Production Tweaks

### 1. Vector DB Caching (in embeddings.py)
- Don’t recompute embeddings on every run.
- Persist them once (Chroma in "db" folder), reload if already there.
- Saves huge compute costs in production.
- **Cached embeddings in a persistent vector DB so they’re computed only once, queries just reuse it, which saves time and resources.**

### 2. Quantization (in llm.py)
- int8 quantization (bitsandbytes) → cuts GPU memory, improves latency.
- Torch compile (PyTorch 2.0+) → graph optimization for faster inference.
- **Applied `int8 quantization` or `torch.compile` to reduce memory footprint and speed up inference without major accuracy loss**

### 3. Batch Inference (in llm.py)
- Use batch_size=8 in Hugging Face pipeline.
- Handles multiple queries in parallel, improving throughput under load
- **Supported batched inference in the pipeline so multiple user queries can be processed in one forward pass**

 ### 4. Fallbacks (in llm.py)
 - Add fallback model:
   - GPU busy → smaller CPU model.
   - Large model too slow → use flan-t5-base
 - **Added a timeout for robustness, and if the GPU is overloaded, fall back to a smaller CPU model for graceful degradation**

### 5. Metadata Filtering (in chain.py).
- Extended `build_qa_chain` to optionally accept filters, so it works in two modes:
  - Default: Just retrieves top-k chunks.
  - With filter: Only retrieves chunks that match metadata conditions.

### 6. Guardrails via Prompt Instructions (in QA_PROMPT).
- Guardrails in RAG = rules put in place to:
  - Control style (2–3 sentences, full stop).
  - Control content (no hallucinated emails, citations, links).
  - Control failure mode (“I don’t know from the document.”).

 ### 7. Model Caching (in fastapi_app.py)
 - Load LLM once at startup (FastAPI app startup).
 - Avoids repeated heavy initialization.
 - **Cached the LLM pipeline at app startup, so inference requests reuse the same model object, reducing latency**

### 8. Timeouts (in FastAPI /query endpoint)
- Add timeout per query (avoid hanging requests).
  
----

## Future Production Steps

- Containerization (Docker) and maybe orchestration (Kubernetes)
- Monitoring/logging (Prometheus, Grafana, or even just better logs)
- Deployment pipeline (CI/CD with GitHub Actions, AWS/GCP/Azure hosting)
- Auth/security for endpoints
- Load testing (e.g. locust or k6)
- Scaling (workers, async inference, caching)
