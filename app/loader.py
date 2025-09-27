# app/loader.py
# Step 1: PDF loading + chunking

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load PDF
loader = PyPDFLoader("/content/RAG_Paper.pdf")
documents = loader.load()

# Filter out reference/appendix pages
filtered_docs = [
    doc for doc in documents
    if not any(x in doc.page_content for x in ["References", "Appendix", "Limitations", "Ethics"])
]

# Split into smaller chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)
chunks = splitter.split_documents(filtered_docs)
print(f"Total chunks after filtering: {len(chunks)}")
