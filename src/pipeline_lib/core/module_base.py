import abc

class PipelineModule(abc.ABC):
    @abc.abstractmethod
    def run(self,data): 
        pass