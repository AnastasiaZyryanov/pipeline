import json
from .validator import validate_config

def load_config(path: str):
    with open(path) as f:
        data = json.load(f)
    validate_config(data)
    return data

def save_config(config, path):
    validate_config(config)

    with open(path, "w") as f:
        json.dump(config, f, indent=2)