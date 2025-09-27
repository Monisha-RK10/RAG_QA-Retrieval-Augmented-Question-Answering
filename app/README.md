# Functionality of Scripts 

| File            | Role                                                                                                                                                                                                 |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `loader.py`     | Load PDFs and split them into chunks. Each chunk is a piece of text that the embeddings model can work on.                                                                                           |
| `embeddings.py` | Take the chunks, convert them into embeddings, and store them in a vector database (Chroma). This is what lets the RAG system **retrieve relevant chunks** for a query.                              |
| `llm.py`        | Load your language model (Flan-T5) as a pipeline that will generate answers from the retrieved chunks.                                                                                               |
| `chain.py`      | Define the **RetrievalQA chain**, which links the retriever (vector DB) and LLM, plus your prompt template. This is the core RAG logic: "retrieve relevant context → pass to LLM → generate answer". |
