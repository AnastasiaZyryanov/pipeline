from pipeline_lib.config.validator import validate_config
import json

with open("tests/example_config.json") as f:
    data = json.load(f)

validate_config(data)
print("Successfully validated")