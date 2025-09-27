# app/llm.py
# Step 3: Load LLM

# Seq2Seq (Flan-T5)

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
from langchain.llms import HuggingFacePipeline

model_name = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, device_map="auto", torch_dtype="auto")

def load_llm():
    """
    Load the FLAN-T5 model as a HuggingFace pipeline wrapped in LangChain.
    """
    pipe = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    max_length=512,          # shorter cap/let it use full capacity
    min_length=40,           # force some detail/still ensures substance
    num_beams=4,             # beam search (less repetition than greedy)
    no_repeat_ngram_size=3,  # avoid repeated 3-grams
    early_stopping=True,
    truncation=True
)

    return HuggingFacePipeline(pipeline=pipe)
