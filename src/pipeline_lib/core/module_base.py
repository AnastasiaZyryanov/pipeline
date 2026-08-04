import abc

class PipelineModule(abc.ABC):
    @abc.abstractmethod
    def run(self,data): 
        pass

    def get_runner(self):
            return None