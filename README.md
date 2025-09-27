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
  -**Added a timeout for robustness, and if the GPU is overloaded, fall back to a smaller CPU model for graceful degradation**

 ### 5. Model Caching (in fastapi_app.py)
 - Load LLM once at startup (FastAPI app startup).
 - Avoids repeated heavy initialization.
 - **Cached the LLM pipeline at app startup, so inference requests reuse the same model object, reducing latency**

### 6. Timeouts (in FastAPI /query endpoint)
- Add timeout per query (avoid hanging requests).
  
