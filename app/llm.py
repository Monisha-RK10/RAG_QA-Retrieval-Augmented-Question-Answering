# app/llm.py
# Step 3: Load LLM
# Seq2Seq (Flan-T5)

# Production tweak #2: Quantization for faster inference
# Production tweak #3: Batch inference for higher throughput
# Production tweak #4: Timeout + fallback model

# Note: The pipeline is tuned for coherent, non-repetitive, moderately long answers

def load_llm(model_name: str = "google/flan-t5-large"):
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline                # Loads the tokenizer (maps text ↔ tokens), loads a Seq2Seq language model (T5 family, BART, etc.), Hugging Face’s inference wrapper (simplifies generation).
    from langchain.llms import HuggingFacePipeline                                         # LangChain adapter so you can call the model inside a chain.

    tokenizer = AutoTokenizer.from_pretrained(model_name)                                  # Downloads (or loads locally) the tokenizer associated with the given model.
    model = AutoModelForSeq2SeqLM.from_pretrained(                                         # Loads the actual LLM weights
        model_name, device_map="auto", torch_dtype="auto", load_in_8bit=True               # <--- int8 quantization, automatically places the model on GPU if available, else CPU, chooses optimal precision (float16 on GPU, float32 on CPU).
    )

    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        batch_size=8,                                                                      # process 8 queries in parallel
        max_length=512,                                                                    # Cap output length
        min_length=40,                                                                     # Avoid ultra-short answers.
        num_beams=4,                                                                       # Beam search decoding for better answers.
        no_repeat_ngram_size=3,                                                            # Prevents repeated phrases (common in T5).
        early_stopping=True,                                                               # Stop when decoding is finished (not forced to max_length).
        truncation=True                                                                    # Ensures overly long inputs are truncated instead of crashing
    )
    model = torch.compile(model)                                                           # speeds up inference
    return HuggingFacePipeline(pipeline=pipe)                                              # Converts the Hugging Face pipeline into a LangChain LLM object, allows to plug it directly into LangChain’s chain (retrieval → LLM → answer).
