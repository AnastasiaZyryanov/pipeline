import json
from pipeline_lib.core.builder import build_pipeline

with open("tests/example_config.json") as f:
    config = json.load(f)

pipeline = build_pipeline(config)

result = pipeline.run("Pipeline was run successfully")

print(result)