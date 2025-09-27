# app/loader.py
# Step 1: PDF loading + chunking

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from langchain.schema import Document  # for type hints

def load_and_chunk_pdf(pdf_path: str, chunk_size: int = 300, chunk_overlap: int = 100) -> List[Document]:
    """
    Load a PDF, filter out references/appendix pages, and split into chunks.

    Args:
        pdf_path (str): Path to the PDF file.
        chunk_size (int): Max size of each text chunk.
        chunk_overlap (int): Overlap between chunks.

    Returns:
        List[Document]: List of document chunks ready for embeddings/indexing.
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    filtered_docs = [
        doc for doc in documents
        if not any(x in doc.page_content for x in ["References", "Appendix", "Limitations", "Ethics"])
    ]

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(filtered_docs)

    print(f"Total chunks after filtering: {len(chunks)}")
    return chunks
