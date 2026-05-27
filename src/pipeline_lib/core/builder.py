from ..config.validator import validate_config
from .factory import create_module
from ..runner import Pipeline


def build_pipeline(data: dict) -> Pipeline:
    config = validate_config(data)

    order = [
        "Chunker",
        "Cleaner",
        "SentimentAnalyzer",
        "KeywordExtractor"
    ]
    steps = []
    for step_name in order:
        step_cfg = config[step_name]
        module = create_module(step_cfg)
        print(f"[Builder] Created module {module}, runner={getattr(module, 'runner', None)}")
        steps.append(module)  

    return Pipeline(steps)