from ..utils import load_function_from__file
from ..core.module_base import PipelineModule

class Cleaner(PipelineModule):
    def run(self): pass

class NoClean(Cleaner):
    def __init__(self):    
        pass

    def run(self, data):
        print("Run without cleaner")
        return data

class CleanerWithScript(Cleaner):
    def __init__(self, script, entrypoint):
        self.script=script
        self.entrypoint=entrypoint

    def run(self, data):
        print("Run cleaner with script")

        clean_function = load_function_from__file(self.script, self.entrypoint)
        data = data.copy()        
        data["chunk"] = data["chunk"].apply(clean_function)    
        
        return data