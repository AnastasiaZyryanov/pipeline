import importlib
import sys
import os
from tqdm.auto import tqdm

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

def datasetIterator(documents: list[str], system_prompt, user_template):
    for doc in documents:
        yield [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_template.format(text=doc)}
        ]

def callGenerator(client, model, documents: list[str], system_prompt, user_template, max_tokens, temperature=0):
    iterator = datasetIterator(documents, system_prompt, user_template)
    bar = tqdm(iterator, total=len(documents))
    for doc in bar:
        response = client.chat.completions.create(
            model=model,
            messages=doc,
            max_tokens=max_tokens,
            temperature=temperature
        )
        result = response.choices[0].message.content
        bar.set_postfix(result=result)
        yield result