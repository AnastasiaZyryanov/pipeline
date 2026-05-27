from .vllm_server import VLLMServerContextManager
from .modules.LLMRunner import VLLMRunner

class Pipeline:
    def __init__(self, modules):
        self.modules = modules
        self.stats = {
            "chunks_total": 0,
            "chunks_processed": 0
        }

    def run(self, data):
              
        self.data = data
        for module in self.modules:
            module.pipeline = self
            runner = module.get_runner()

            if hasattr(module, 'runner') and module.runner is not None:
                print(f"Using runner: {type(runner).__name__}")
                print(f"Model: {runner.model}")     

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