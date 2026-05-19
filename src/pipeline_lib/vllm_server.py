from contextlib import ContextDecorator
import subprocess
import time
import os
import requests

class VLLMServerContextManager(ContextDecorator):
    def __init__(self, model, device=0, port=8000):
        self.model = model
        self.device = device
        self.port = port
        self.process = None

    def __enter__(self):
        print("Starting vLLM server...")
        os.makedirs("logs", exist_ok=True)
        std_out = open(f"logs/vllm_server_{self.model.replace('/', '_')}_port{self.port}.log", "w")
        std_err = open(f"logs/vllm_server_{self.model.replace('/', '_')}_port{self.port}_error.log", "w")

        self.process = subprocess.Popen([
            "vllm",
            "serve",
            self.model,
            "--port",
            str(self.port)
        ], stdout=std_out, stderr=std_err, env={**os.environ, "CUDA_VISIBLE_DEVICES": str(self.device)})

        while not self.__wait_until_ready():
            time.sleep(10)

        print(f"VLLM server for model {self.model} is running on port {self.port}")
        return self
    
    def __wait_until_ready(self):
        try:
            response = requests.get(f"http://localhost:{self.port}/health")
            return response.status_code == 200
        except requests.ConnectionError:
            return False
        
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print("\n[VLLM ERROR DETECTED]")
            print("Type:", exc_type)
            print("Value:", exc_value)

        print("Stopping vLLM server...")

        if self.process:
            self.process.terminate()
            self.process.wait()
            print(f"VLLM server for model {self.model_name} on port {self.port} has been terminated.")
        return False