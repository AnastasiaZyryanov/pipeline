class Pipeline:
    def __init__(self, modules):
        self.modules = modules

    def run(self, data):
        for module in self.modules:
            data = module.run(data)
        return data