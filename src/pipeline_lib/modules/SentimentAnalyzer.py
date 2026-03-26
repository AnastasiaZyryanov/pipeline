import abc

class SentimentAnalyzer(abc.ABC):
        @abc.abstractmethod
        def run(self): pass

class SAwithLLM:
    def _init_(self, generated_responses, runner, prompt=None,  max_tokens=None):    
        self.prompt=prompt
        self.generated_responses=generated_responses
        self.max_tokens=max_tokens
        self.runner=runner

    @classmethod
    def run(self):
        print("Run sentiment analyzer with LLM")

class SAwithAttention:
    def _init_(self, model):
        self.model=model
                
    @classmethod
    def run(self):
        print("Run sentiment analyzer with attention")