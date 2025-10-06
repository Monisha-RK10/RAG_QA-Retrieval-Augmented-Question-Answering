#  RAG_QA: Retrieval-Augmented Question Answering 

This project implements a Retrieval-Augmented Generation (RAG) pipeline for question answering over PDFs.
It combines vector search + large language models and serves results via a FastAPI backend.

Blog post (concept + pipeline walkthrough):

[RAG Pipeline for Travel Data](https://medium.com/@monishatemp20/rag-2-rag-pipeline-for-travel-data-part-1-41abe0fea2b1)

---

## Pipeline Overview

- Loader → Parse & chunk PDFs into text passages.
- Embeddings + Vector DB → Encode passages, persist them in Chroma.
- Retriever → Retrieve top-k relevant chunks per query.
- LLM → Answer using retrieved context (Flan-T5, quantized for efficiency).
- FastAPI Server → Expose /query, /upload_query, /health endpoints.

---

## Project Structure

```
RAG_QA/
│── app/
|   ├── db_models.py     # SQLAlchemy models + engine setup
│   ├── loader.py        # PDF loading + chunking
│   ├── embeddings.py    # Embeddings + Chroma vectorstore
│   ├── llm.py           # LLM loading + quantization
│   ├── chain.py         # RAG pipeline (retriever + LLM chain)
│   ├── fastapi_app.py   # API endpoints
│   |── settings.py      # Pydantic BaseSettings class that loads/validates config
│   └── tests/
│       └── test_api.py  # Unit + integration tests
│       └── test_db.py   # To confirm Postgres connection works inside docker-compose
|
│── documents/           # Explains process & implementation rollout for production via different phases
│── db/                  # Persisted vectorstore
│── data/                # Temp data / scratch (pdf files)
│── requirements.txt
│── README.md            # This file
│── Dockerfile           # To make app portable, reproducible
│── docker-compose.yml   # To run multiple containers as a system (FastAPI, Postgres, maybe Redis).
│── config.yaml          # Central configuration file for models, directories, and database


```
## Production Tweaks Implemented

1. **Vector DB Caching** → Persist embeddings once, reuse later.
2. **Quantization + Torch Compile** → Faster inference, lower memory.
3. **Batch Inference** → Process multiple queries in parallel.
4. **Fallback Models** → Graceful degradation if GPU unavailable.
5. **Metadata Filtering** → Restrict retrieval by document metadata.
6. **Prompt Guardrails** → Style/content control, safe fallback answers.
7. **Model Caching at Startup** → No repeated heavy init per request.
8. **Timeouts** → Prevent hanging requests.

---

## Future Steps

- Containerization (Docker, Kubernetes)
- Monitoring/logging (Prometheus, Grafana)
- CI/CD deployment pipeline
- Auth/security for endpoints
- Load testing (locust, k6)
- Async scaling for high throughput

---
 
## Output: Example Queries & Responses

**Q: What is Effect of Retrieving more documents?**

**A:** improves documents, and we do not observe significant differences in performance between them. We have the flexibility to adjust the number of retrieved documents at test time, which can affect performance and runtime.

**Q: What is seq2seq model?**

**A:** p(y|x) via a top-K approximation. Concretely, the top K documents are retrieved using the retriever, and the generator produces the output sequence probability for each document, which are then marginalized.

**Q: What is Open-domain Question Answering?**

**A:** an important real-world application and common testbed for knowledge-intensive tasks. We treat questions and answers as input-output text pairs (x,y) data. We now discuss experimental details for each task.

**Q: What is the advantage of Index hot-swapping?**

**A:** knowledge can be easily updated at test time. Parametric-only models like T5 or BART need further training to improves results on all other tasks, especially for Open-Domain QA, where it is crucial.

---


## Author

**Monisha**  
Connect via [Medium](https://medium.com/@monishatemp20)  [Linkedin](https://www.linkedin.com/in/monisha-rao-28129676/)

---
