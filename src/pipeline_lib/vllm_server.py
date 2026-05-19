from contextlib import ContextDecorator
import subprocess
import time
import requests

class VLLMServerContextManager(ContextDecorator):
    def __init__(self, model, device=0, port=8000):
        self.model = model
        self.device = device
        self.port = port
        self.process = None

    def __enter__(self):
        print("Starting vLLM server...")

        self.process = subprocess.Popen([
            "python", "-m", "vllm.entrypoints.openai.api_server",
            "--model", self.model,
            "--port", str(self.port),
            "--device", str(self.device)
        ])

        time.sleep(5) 
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Stopping vLLM server...")
        if self.process:
            self.process.terminate()