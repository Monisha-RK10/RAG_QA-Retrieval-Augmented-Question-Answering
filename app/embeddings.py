# app/embeddings.py
# Step 2: Create Embeddings and Vector DB

# Production tweak #1: Vector DB persistence, ensures embeddings are computed once and reused across runs.

# Note: For vector DB in production,
# First run: You upload a PDF → chunks → embeddings → vectorstore created in db/.
# Later runs: DB already exists → no chunking/embedding → queries are super fast.

from langchain.embeddings import HuggingFaceEmbeddings                                               # Imports LangChain’s wrapper around Hugging Face sentence-transformers
from langchain_community.vectorstores import Chroma                                                  # Imports Chroma, an open-source vector database that stores embeddings and lets you run similarity searches (kNN). Chroma here is LangChain’s integration, not raw ChromaDB API.
from langchain.schema import Document                                                                # List of LangChain `Document` objects (from `loader.py`).
from typing import List
import os

#from app.settings import settings

def load_or_create_vectorstore(
    chunks: List[Document] = None,
    model_name: str = "all-MiniLM-L6-v2",                                                            # A small, fast sentence-transformer model, 384-dim embeddings, You can replace with larger models (e.g., `"all-mpnet-base-v2"`).  
   # model_name: str = settings.embedding_model,
    persist_directory: str = "db"                                                                    # Directory where Chroma will save the database files. Default `"db"`. 
) -> Chroma:                                                                                         # ChromaDB: Pure Python, stores vectors + metadata + documents together, has persistence (saves to disk), so DB survives kernel restarts. Good for prototyping, for production with millions of docs, move to FAISS, Pinecone, or Weaviate.
    """
    Load an existing Chroma vectorstore if it exists,
    otherwise create it from the provided chunks.

    Args:
        chunks (List[Document], optional): Document chunks from loader.
            Required only when creating a new DB.
        model_name (str): HuggingFace embedding model.
        persist_directory (str): Directory where DB is stored.

    Returns:
        Chroma: Vectorstore instance.
    """
    embeddings = HuggingFaceEmbeddings(model_name=model_name)                                        # Each text chunk will be fed into this model → returns a vector of floats. SentenceTransformer library already handles tokenization internally (it automatically tokenizes, pads, feeds into encoder, and returns the vector). Embeddings create “semantic memory.” & LLM interprets query + memory, produces natural language answers.

    # Case 1: DB already exists -> just load it                                                      # Pre-created an empty db/ folder (good practice in production)
    if os.path.exists(os.path.join(persist_directory, "index")):                                     # index: internal data structure that maps embeddings → positions in vector space so similarity search is fast. Check if Chroma’s index files are already inside db/, if yes, don’t recompute anything. This saves time, GPU/CPU, and prevents duplicate embeddings being created each run.
        vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        print(f"Loaded existing vectorstore from {persist_directory}")
        return vectordb

    # Case 2: No DB yet -> need chunks to build it
    if chunks is None:                                                                               # If DB does not exist, need to build, ensure chunk is passed
        raise ValueError(
            "No existing DB found and no chunks provided to create one."
        )

    vectordb = Chroma.from_documents(                                                                # 1) Runs `embeddings` on each `Document.page_content`, 2) Stores the resulting vectors + document metadata in the Chroma DB, 3) Saves DB files into `persist_directory`. Note: If `"db"` exists, Chroma will load from it; if not, it creates it. This makes your embeddings persistent across runs.
        chunks,
        embeddings,                                                                                                        
        persist_directory=persist_directory
    )
    print(f"Created new vectorstore at {persist_directory}")
    return vectordb                                                                                  # Returns the Chroma vector DB instance, which will be used in later steps for retrieval during QA.
