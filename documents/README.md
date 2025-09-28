# Process (prototype → modular → production tweaks)

### 1. Prototype stage → get something working end-to-end, even if rough (one PDF, no modularity, no caching).

- This proves feasibility.
- Lightweight, no over-engineering.

### 2. Refactor/modularize → split into loader.py, llm.py, embeddings.py, chain.py, fastapi_app.py.
- Now it’s testable, maintainable, extendable.

### 3. Production hardening → caching, quantization, batch inference, fallbacks, timeouts, metadata filtering.
- These are system-level engineering concerns: reliability, performance, scaling, robustness.

### 4. Testing + FastAPI serving → run unit/integration tests on Colab by cloning the GitHub repo.
- This is for CI/CD thinking (currently, treating Colab like a staging environment).
