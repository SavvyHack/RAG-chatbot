import logging

logger = logging.getLogger(__name__)

_llm_model = None
_llm_tokenizer = None

def get_llm():
    global _llm_model, _llm_tokenizer
    if _llm_model is None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        model_name = "Qwen/Qwen2.5-1.5B-Instruct"
        logger.info(f"Loading LLM {model_name} (first request)...")
        
        _llm_tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        _llm_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
            trust_remote_code=True
        )
    return _llm_tokenizer, _llm_model

def generate_response(context_chunks, query):
    tokenizer, model = get_llm()
    
    context_str = "\n\n".join(context_chunks) if context_chunks else "No additional context provided."
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Answer the user's question based on the provided context. If the context does not contain the answer, say so."},
        {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {query}"}
    ]
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512,
        temperature=0.7,
        do_sample=True
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response