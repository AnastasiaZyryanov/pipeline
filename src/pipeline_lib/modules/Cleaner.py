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

        clean_function = self.load_function_from__file(self.script, self.entrypoint)
        data = data.copy()        
        data["chunk"] = data["chunk"].apply(clean_function)          
        return data
        
    def  load_function_from__file(self, path, function_name):
        if not os.path.exists(path):
                raise FileNotFoundError(f"The {path} does not exist.")
        module_name="user_module_"+os.path.basename(path).split('.')[0]
        import importlib
        import sys
        import os
        spec=importlib.util.spec_from_file_location(module_name, path)
        module=importlib.util.module_from_spec(spec)
        sys.modules[module_name]=module
        spec.loader.exec_module(module)
        if hasattr(module, function_name):
            return getattr(module, function_name)
        else: 
            raise AttributeError(f"Function {function_name} not found at {path}")