import json
from pipeline_lib.core.builder import build_pipeline

with open("tests/example_config.json") as f:
    config = json.load(f)

pipeline = build_pipeline(config)

input_data = "Test completed successfully"

result = pipeline.run(input_data)

print("FINAL RESULT:")
print(result)