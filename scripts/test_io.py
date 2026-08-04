from pipeline_lib.config.io import load_config, save_config

config = load_config("scripts/model_1.json")

print(config)

save_config(config, "scripts/copy.json")