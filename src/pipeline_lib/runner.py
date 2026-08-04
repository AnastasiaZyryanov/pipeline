from .servers.vllm_server import VLLMServerContextManager
from .modules.LLMRunner import VLLMRunner

class Pipeline:
    def __init__(self, modules):
        self.modules = modules
        
    def run(self, data):
              
        self.data = data
        for module in self.modules:
            module.pipeline = self
            runner = getattr(module, "runner", None)

            # if runner is not None:
            #     print(f"Using runner: {type(runner).__name__}")
            #     print(f"Model: {runner.model}")    

            if isinstance(runner, VLLMRunner):
                with VLLMServerContextManager(
                    model=runner.model,
                    device=runner.gpu,
                    port=runner.port
                ):
                    data = module.run(data)
            else:
                data = module.run(data)

        return data                