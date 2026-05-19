import abc
from ..utils import callGenerator
import ollama
import openai
from ..vllm_server import VLLMServerContextManager

class LLMRunner(abc.ABC):
    def __init__(self, model, api_key=None, seed=None): 
        self.model=model
        self.api_key=api_key
        self.seed=seed
        

    @abc.abstractmethod
    def generate(self, documents, system_prompt, user_template, max_tokens, temperature=0):
        pass    

class OllamaRunner(LLMRunner):
    def __init__(self, model, api_key=None, seed=None): #, gpu=None, port=None):
        super().__init__(model, api_key, seed) 
        # self.gpu=gpu
        # self.port=port
        self.client = None
        self._server = None
    
    def generate(self, documents, system_prompt, user_template, max_tokens, temperature=0):
        results = []

        for doc in documents:
            response = ollama.generate(
                model=self.model, prompt=f"{system_prompt}\n\n{user_template.format(text=doc)}", options={'temperature': temperature, 'num_predict': max_tokens}, 
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

    def generate(self, documents, system_prompt, user_template, max_tokens, temperature=0):
        with VLLMServerContextManager(model=self.model, device=self.gpu, port=self.port)  as vllm_process: #as server:
            client = openai.OpenAI(base_url=f"http://localhost:{self.port}/v1", api_key=self.api_key or "EMPTY")
        return list(callGenerator(client, self.model, documents, system_prompt, user_template, max_tokens, temperature))
