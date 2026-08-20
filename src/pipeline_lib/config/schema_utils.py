from .schema import PIPELINE_SCHEMA


def resolve_ref(ref: str) -> dict:
    name = ref.split("/")[-1]
    return PIPELINE_SCHEMA["$defs"][name]

def get_module_schema(module_name):
    return resolve_ref(PIPELINE_SCHEMA["properties"][module_name]["$ref"])

def get_available_types(schema):
    schema = resolve_schema(schema)
    result = []
    for variant in schema.get("oneOf", []):
        variant = resolve_schema(variant)
        props = variant.get("properties", {})
        type_schema = props.get("type", {})
        const = type_schema.get("const")
        if const:
            result.append(const)

    return result

def get_schema_for_type(schema, type_name):
    schema = resolve_schema(schema)
    for variant in schema["oneOf"]:
        variant = resolve_schema(variant)
        if variant["properties"]["type"]["const"] == type_name:
            return variant
    raise ValueError(type_name)

def get_properties(schema):
    schema = resolve_schema(schema)
    return schema.get("properties", {})

def get_required_fields(module_name: str, type_name: str) -> list[str]:
    schema = get_schema_for_type(
        module_name,
        type_name
    )
    return schema.get("required", [])

def resolve_schema(schema):
    if "$ref" in schema:
        return resolve_schema(
            resolve_ref(schema["$ref"])
        )
    if "allOf" in schema:
        merged = {"type": "object","properties": {},"required": []}
        for part in schema["allOf"]:
            part = resolve_schema(part)
            merged["properties"].update(part.get("properties", {}))
            merged["required"].extend(part.get("required", []))
        return merged
    return schema

def get_oneof_variants(schema):
    schema = resolve_schema(schema)
    variants = []
    if "oneOf" not in schema:
        return variants
    for variant in schema["oneOf"]:
        resolved = resolve_schema(variant)
        type_name = resolved["properties"]["type"]["const"]
        variants.append((type_name, resolved))
    return variants

def get_pipeline_modules():
    return list(PIPELINE_SCHEMA["properties"].keys())