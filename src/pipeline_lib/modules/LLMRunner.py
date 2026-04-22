import abc

class LLMRunner(abc.ABC):
    @abc.abstractmethod
    def run(self): pass

class OllamaRunner(LLMRunner):
    def __init__(self, gpu=None, port=None):    
        self.gpu=gpu
        self.port=port


    def run(self, data):
        print("OllamaRunner")
        return data

class VLLMRunner(LLMRunner):
    def __init__(self, gpu=None, port=None):    
        self.gpu=gpu
        self.port=port

    def run(self, data):
        print("VLLMRunner")
        return data