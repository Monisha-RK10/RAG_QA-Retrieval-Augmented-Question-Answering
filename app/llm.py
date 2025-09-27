# app/llm.py
# Step 3: Load LLM
# Seq2Seq (Flan-T5)

def load_llm(model_name: str = "google/flan-t5-large"):
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
    from langchain.llms import HuggingFacePipeline

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name, device_map="auto", torch_dtype="auto"
    )

    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=512,
        min_length=40,
        num_beams=4,
        no_repeat_ngram_size=3,
        early_stopping=True,
        truncation=True
    )

    return HuggingFacePipeline(pipeline=pipe)
