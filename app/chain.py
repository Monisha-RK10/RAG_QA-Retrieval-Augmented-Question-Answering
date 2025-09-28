# app/chain.py
# Step 4: Prompt integration + Flexible retrieval

from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain.schema import BaseRetriever
from langchain.llms.base import LLM

template = """You are an expert assistant answering questions based only on the provided context.        # Defines style & constraints of LLM answers (fact-based, complete sentences).

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



QA_PROMPT = PromptTemplate.from_template(template)                                                       # LangChain’s PromptTemplate wrapper.

def build_qa_chain(llm: LLM, vectordb: BaseRetriever, k: int = 3) -> RetrievalQA:                        # Wraps LLM + retriever into a RetrievalQA chain
    """
    Build a RetrievalQA chain from the LLM and vector database.
    """
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": k})                  # Uses similarity search, top-3 docs.
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,                                                                    # Returns both answer + source documents (important for transparency).
        chain_type_kwargs={"prompt": QA_PROMPT}
    )
    return qa_chain
