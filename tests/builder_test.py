from pipeline_lib.core.builder import build_pipeline
import json

config = json.load(open("tests/example_config.json"))

pipeline = build_pipeline(config)

print("Created pipeline:")
print(type(pipeline))
print("with modules: ")
print(pipeline.modules)