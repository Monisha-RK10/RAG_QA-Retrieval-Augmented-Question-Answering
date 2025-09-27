# app/embeddings.py
# Step 2: Embedding
# Create Embeddings and Vector DB

from langchain.embeddings import HuggingFaceEmbeddings                                               # Imports LangChain’s wrapper around Hugging Face sentence-transformers
from langchain_community.vectorstores import Chroma                                                  # Imports Chroma, an open-source vector database that stores embeddings and lets you run similarity searches (kNN). Chroma here is LangChain’s integration, not raw ChromaDB API.
from langchain.schema import Document
from typing import List

def create_vectorstore(
    chunks: List[Document],                                                                          # List of LangChain `Document` objects (from `loader.py`).
    model_name: str = "all-MiniLM-L6-v2",                                                            # A small, fast sentence-transformer model, 384-dim embeddings, You can replace with larger models (e.g., `"all-mpnet-base-v2"`).  
    persist_directory: str = "db"                                                                    # Directory where Chroma will save the database files. Default `"db"`.  
) -> Chroma:
    """
    Create embeddings and initialize a Chroma vectorstore.

    Args:
        chunks (List[Document]): List of document chunks from loader.
        model_name (str): Embedding model name.
        persist_directory (str): Directory to save the vectorstore.

    Returns:
        Chroma: Vectorstore instance.
    """
    embeddings = HuggingFaceEmbeddings(model_name=model_name)                                        # Each text chunk will be fed into this model → returns a vector of floats. 
    vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=persist_directory)        # 1) Runs `embeddings` on each `Document.page_content`, 2) Stores the resulting vectors + document metadata in the Chroma DB, 3) Saves DB files into `persist_directory`. Note: If `"db"` exists, Chroma will load from it; if not, it creates it. This makes your embeddings persistent across runs.

    return vectordb                                                                                  # Returns the Chroma vector DB instance, which will be used in later steps for retrieval during QA.

