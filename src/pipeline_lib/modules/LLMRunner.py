import abc
from ..servers.ollama_server import OllamaServer
import ollama
import openai
from tqdm.auto import tqdm

class LLMRunner(abc.ABC):
    def __init__(self, model, api_key=None, seed=None): 
        self.model=model
        self.api_key=api_key
        self.seed=seed
   
    @abc.abstractmethod   
    def generate(self, documents, system_prompt, user_template, max_tokens, temperature=0):
        pass    

class OllamaRunner(LLMRunner):
    def __init__(self, model, api_key=None, seed=None): 
        super().__init__(model, api_key, seed) 
        self.server = OllamaServer()
        self.server.ensure_running()
        self.client = ollama.Client()
        self.ensure_model_exists()

    def ensure_model_exists(self):
        installed_models = [m["model"].split(':')[0] for m in ollama.list()["models"]]        
        if self.model not in installed_models:
            #print(f"Pulling Ollama model: {self.model}")
            ollama.pull(self.model)        
        print(f"Model: {self.model}")
  
    def generate(self, documents, system_prompt, user_template, max_tokens, temperature=0, **kwargs):
        generated_responses = kwargs.get('generated_responses', None)
        results = []
        for doc in documents:
            if generated_responses is not None:
                doc_responses = []
                for _ in range(generated_responses):
                    response = ollama.generate(
                        model=self.model,
                        prompt=f"{system_prompt}\n\n{user_template.format(text=doc)}",
                        options={'temperature': temperature, 'num_predict': max_tokens}
                    )
                    doc_responses.append(response['response'].strip())
                results.append(doc_responses)
            else:
                response = ollama.generate(
                    model=self.model,
                    prompt=f"{system_prompt}\n\n{user_template.format(text=doc)}",
                    options={'temperature': temperature, 'num_predict': max_tokens}
                )
                results.append(response['response'].strip())
        return results

class VLLMRunner(LLMRunner):
    def __init__(self, model, api_key=None, seed=None, gpu=None, port=None):
        super().__init__(model, api_key, seed)    
        self.gpu=gpu
        self.port=port
        self.client = None
        self._server = None

    def generate(self, documents, system_prompt, user_template, max_tokens, generated_responses=None, temperature=None):
        if self.client is None:
            self.client=openai.OpenAI(
                base_url=f"http://localhost:{self.port}/v1",
                api_key=self.api_key or "EMPTY"
            )
        return list(self.callGenerator(self.client, self.model, documents, system_prompt, user_template, max_tokens, temperature, generated_responses))  
          
    
    def datasetIterator(self, documents: list[str], system_prompt, user_template):
        for doc in documents:
            if isinstance(doc, dict):
                content = user_template.format(**doc)
            else:
                content = user_template.format(text=doc)
            yield [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]

    def callGenerator(self, client, model, documents: list[str], system_prompt, user_template, max_tokens=None, temperature=None, generated_responses=None):
        if system_prompt is None:
            system_prompt = ""
        if user_template is None:
            user_template = ""
    
        iterator = self.datasetIterator(documents, system_prompt, user_template)    
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