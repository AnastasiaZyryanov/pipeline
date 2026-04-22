import abc

class SentimentAnalyzer(abc.ABC):
        @abc.abstractmethod
        def run(self): pass

class SAwithLLM(SentimentAnalyzer):
    def __init__(self, generated_responses, runner, prompt=None,  max_tokens=None):    
        self.prompt=prompt
        self.generated_responses=generated_responses
        self.max_tokens=max_tokens
        self.runner=runner

    def run(self, data):
        print("Run sentiment analyzer with LLM")
        return data

class SAwithAttention(SentimentAnalyzer):
    def __init__(self, model):
        self.model=model
                
    def run(self, data):
        print("Run sentiment analyzer with attention")
        return data