#from contextlib import ExitStack
from .vllm_server import VLLMServerContextManager
from .modules.LLMRunner import VLLMRunner

class Pipeline:
    def __init__(self, modules):
        self.modules = modules
        self.stats = {
            "chunks_total": 0,
            "chunks_processed": 0
        }

    def _collect_runners(self):
        runners = []
        for module in self.modules:
            runner = module.get_runner()
            if runner is not None:
                runners.append(runner)
        return runners

    def _start_vllm_servers(self, stack):
        started = set()
        for runner in self._collect_runners():
            if not isinstance(runner, VLLMRunner):
                continue
            key = (runner.model, runner.gpu, runner.port)
            if key in started:
                continue
            started.add(key)
            stack.enter_context(
                VLLMServerContextManager(
                    model=runner.model,
                    device=runner.gpu,
                    port=runner.port
                )
            )

    def run(self, data):
        # with ExitStack() as stack:
        #     self._start_vllm_servers(stack)
        #     self.data = data
        #     for module in self.modules:
        #         module.pipeline = self
        #         data = module.run(data)        
        self.data = data
        for module in self.modules:
            module.pipeline = self
            runner = module.get_runner()

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