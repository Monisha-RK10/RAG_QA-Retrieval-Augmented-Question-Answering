# app/chain.py
# Step 4: Prompt integration + Flexible retrieval
# Production tweak #5: Metadata filtering support
# Production tweak #6: Guardrails via prompt instructions (in QA_PROMPT).

# Context flow (the retrieval → generation loop of RAG):
# User asks a question → passed into qa_chain.
# Retriever pulls context (top-3 relevant chunks).
# LangChain fills the prompt template with {context} + {question}.
# This structured input goes into the LLM (llm.py).
# Output: Answer (shaped by template rules) + Source docs (for traceability).

from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain.schema import BaseRetriever
from langchain.llms.base import LLM

# Defines style & constraints of LLM answers (fact-based, complete sentences).
template = """You are an expert assistant answering questions based only on the provided context.        

Instructions:
- Always answer in 2–3 full sentences, clearly and factually.
- Summarize in your own words. Do NOT copy emails, author lists, citations, or raw links.
- If the document does not contain the answer, reply only: "I don't know from the document."
- Avoid incomplete sentences and repetition.
- All answers must end with a full sentence.

Context:
{context}

Question:
{question}

Answer:"""

QA_PROMPT = PromptTemplate.from_template(template)                                                                # LangChain’s PromptTemplate wrapper.

def build_qa_chain(llm: LLM, vectordb: BaseRetriever, k: int = 3, metadata_filter: dict = None) -> RetrievalQA:   # Wraps LLM + retriever into a RetrievalQA chain                     
    """
    Build a RetrievalQA chain from the LLM and vector database.

    Args:
        llm (LLM): The language model.
        vectordb (BaseRetriever): The vector database retriever.
        k (int): Number of top chunks to retrieve.
        metadata_filter (dict, optional): Metadata filter for narrowing search (e.g., {"section": "Introduction"}).
        
    """
    search_kwargs = {"k": 3}
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter                                                                 # Only pass filter when you actually have metadata to filter on. If metadata_filter is empty or None:, search_kwargs = {"k": 3}, no "filter" key at all. If later you do pass a real filter, e.g., metadata_filter = {"section": "methods"} then search_kwargs becomes: {"k": 3, "filter": {"section": "methods"}} and Chroma accepts it. Else, ValueError: Expected where to have exactly one operator, got {}
    retriever = vectordb.as_retriever(
        search_type="similarity",                                                                                 # It computes embeddings for the query and finds the k nearest neighbors in vector space (cosine similarity, dot product, etc.).
        search_kwargs=search_kwargs                                                                               # Similarity search = KNN with a similarity metric, mechanism inside similarity search.
    )                                                                                                             # Uses similarity search, top-3 docs. Fast, simple, scalable, perfect for MVPs. 
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,                                                                                                  # LLM itself (loaded in llm.py)
        retriever=retriever,                                                                                      # Retriever wrapping the vector DB (from embeddings.py)
        return_source_documents=True,                                                                             # Returns both answer + source documents (important for transparency).
        chain_type_kwargs={"prompt": QA_PROMPT}                                                                   # Injects the custom prompt template
    )
    return qa_chain
