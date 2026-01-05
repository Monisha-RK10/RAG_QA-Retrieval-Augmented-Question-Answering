# app/loader.py
# Step 1: PDF loading + chunking

from langchain_community.document_loaders import PyPDFLoader                                                   # Reads the PDF and returns a list of Document objects (usually one per page). Each Document has at least page_content (string) and metadata (dict, often includes source and page number).
#from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
#from langchain.schema import Document                                                                          # To annotate the return type and help editors/linters, for type hints
from langchain_core.documents import Document

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
    bad = {"references","appendix","limitations","ethics"}
    filtered_docs = [d for d in documents if not any(k in d.page_content.lower() for k in bad)]                # Take each page d in documents, and keep it only if it does NOT mention references, appendix, limitations, or ethics.

    assert chunk_overlap < chunk_size, "chunk_overlap must be less than chunk_size"

  #  filtered_docs = [
  #      doc for doc in documents
  #      if not any(x in doc.page_content for x in ["References", "Appendix", "Limitations", "Ethics"])
  #  ]

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)              # Recursive splitter attempts to split on natural boundaries (double newlines, sentences, punctuation) before falling back to character splits.
    chunks = splitter.split_documents(filtered_docs)

    # ---- Add metadata ----
    for chunk in chunks:
        page = chunk.metadata.get("page", None)                                                                # Fetches the page number from metadata.
        if page is not None:
            if page <= 1:                                                                                      # Then it assigns a custom section label based on that page number.
                chunk.metadata["section"] = "Introduction"
            elif page <= 3:
                chunk.metadata["section"] = "Methods"
            else:
                chunk.metadata["section"] = "Results"

    print(f"Total chunks after filtering: {len(chunks)}")
    return chunks
