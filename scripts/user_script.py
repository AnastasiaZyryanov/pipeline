import json
import pandas as pd
from pipeline_lib.core.builder import build_pipeline

def main():
    config_path = input("Enter path to config JSON: ")

    with open(config_path) as f:
        config = json.load(f)

    pipeline = build_pipeline(config)

    input_data = "data/comments.csv"
    df = pd.read_csv(input_data)

    result=pipeline.run(df)
    result.to_json("data/output.json", orient="records", lines=True, index=False)
    print("Done")
     

if __name__ == "__main__":
    main()