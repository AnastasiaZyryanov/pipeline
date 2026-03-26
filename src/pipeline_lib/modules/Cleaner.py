import abc

class Cleaner(abc.ABC):
    @abc.abstractmethod
    def run(self): pass

class NoClean:
    def _init_(self):    
        pass

    @classmethod
    def run(self):
        print("Run without cleaner")

class CleanerWithScript:
    def _init_(self, script, entrypoint=None):
        self.script=script
        self.entrypoint=entrypoint
        
    @classmethod
    def run(self):
        print("Run cleaner with script")