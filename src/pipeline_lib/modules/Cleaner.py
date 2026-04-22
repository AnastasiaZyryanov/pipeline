import abc

class Cleaner(abc.ABC):
    @abc.abstractmethod
    def run(self): pass

class NoClean(Cleaner):
    def __init__(self):    
        pass

    def run(self, data):
        print("Run without cleaner")
        return data

class CleanerWithScript(Cleaner):
    def __init__(self, script, entrypoint=None):
        self.script=script
        self.entrypoint=entrypoint
        
    def run(self, data):
        print("Run cleaner with script")
        return data