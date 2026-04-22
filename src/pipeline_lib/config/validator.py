from jsonschema import validate, ValidationError
from .schema import PIPELINE_SCHEMA


def validate_config(data: dict) -> dict:
    try:
        validate(instance=data, schema=PIPELINE_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Invalid config: {e.message}")

    return data