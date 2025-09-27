# app/embeddings.py
# Step 2: Embedding
# Create Embeddings and Vector DB

from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List

def create_vectorstore(
    chunks: List[Document],
    model_name: str = "all-MiniLM-L6-v2",
    persist_directory: str = "db"
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
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=persist_directory)

    return vectordb
