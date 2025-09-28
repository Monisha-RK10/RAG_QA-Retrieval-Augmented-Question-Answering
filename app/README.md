# app/

| File            | Role                                                                                                                                                                                                 |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `loader.py`     | Loads PDF, filters unwanted pages, chunks into overlapping text segments.                                                                                           |
| `embeddings.py` |Converts those chunks into embeddings using HuggingFace model, stores them in a Chroma vector DB for retrieval.                              |
| `llm.py`        | Load your language model (Flan-T5) as a pipeline that will generate answers from the retrieved chunks.                                                                                               |
| `chain.py`      | Define the **RetrievalQA chain**, which links the retriever (vector DB) and LLM, plus your prompt template. This is the core RAG logic: "retrieve relevant context → pass to LLM → generate answer". |
