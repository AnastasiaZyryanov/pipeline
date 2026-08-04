import subprocess
import time
import atexit
import requests

class OllamaServer:
    _instance = None
    _process = None
    _started = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def ensure_running(self):
        if self._started and self._is_running():
            print(f"Ollama server is running")
            return  
        if self._process and self._process.poll() is None:
            return  
        #print("Starting Ollama server...")
        self._process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        for i in range(30):
            if self._is_running():
                #print(f"Ollama server ready after {i+1} seconds")
                self._started = True
                break
            time.sleep(1)
        else:
            raise RuntimeError("Ollama server did not start within 30 seconds")
        atexit.register(self.stop)

    def _is_running(self):
        try:
            r = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
            return r.status_code == 200
        except:
            return False

    def stop(self):
        if self._process and self._process.poll() is None:
            #print("Stopping Ollama server...")
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._started = False
            #print("Ollama server stopped")