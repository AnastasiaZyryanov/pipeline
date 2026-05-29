import importlib
import sys
import os
from tqdm.auto import tqdm
import nltk

def  load_function_from__file(path, function_name):
   if not os.path.exists(path):
        raise FileNotFoundError(f"The {path} does not exist.")
   module_name="user_module_"+os.path.basename(path).split('.')[0]
   spec=importlib.util.spec_from_file_location(module_name, path)
   module=importlib.util.module_from_spec(spec)
   sys.modules[module_name]=module
   spec.loader.exec_module(module)
   if hasattr(module, function_name):
       return getattr(module, function_name)
   else: 
       raise AttributeError(f"Function {function_name} not found at {path}")
   
def split_long_chunk(text, max_tokens=480):       
    # 1 token ≈ 0.75 words,  1 word ≈ 1.33 tokens
    words = text.split()
    estimated_tokens = len(words) * 1.33
    if estimated_tokens <= max_tokens:
        return [text]
    chunk_size_words = int(max_tokens / 1.33)
    if chunk_size_words < 1:
        chunk_size_words = 1
    chunks = []
    for i in range(0, len(words), chunk_size_words):
        chunk = ' '.join(words[i:i+chunk_size_words])
        chunks.append(chunk)
    return chunks

def datasetIterator(documents: list[str], system_prompt, user_template):
    for doc in documents:
        yield [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_template.format(**doc)}
        ]

def callGenerator(client, model, documents: list[str], system_prompt, user_template, max_tokens=None, temperature=None, generated_responses=None):
    if system_prompt is None:
        system_prompt = ""
    if user_template is None:
        user_template = ""
   
    iterator = datasetIterator(documents, system_prompt, user_template)    
    bar = tqdm(iterator, total=len(documents))
    for doc in bar:   
        kwargs = {
            "model": model,
            "messages": doc
        }    
        if temperature is not None:
            kwargs["temperature"] = temperature        
        if generated_responses is not None:
            kwargs["n"] = generated_responses
        if max_tokens is not None:
            kwargs["max_tokens"]= max_tokens

        response = client.chat.completions.create(**kwargs)
        response = [choice.message.content for choice in response.choices]
        bar.set_postfix(result=response)        
        
        yield response

def score_to_label(score):
        if score <= -1.5:
            return "Very Negative"
        elif score <= -0.5:
            return "Negative"
        elif score < 0.5:
            return "Neutral"
        elif score < 1.5:
            return "Positive"
        else:
            return "Very Positive"