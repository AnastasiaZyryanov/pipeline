from pipeline_lib.config.schema_utils import *

print(get_available_types("Chunker"))

print(get_properties("Chunker","SemanticChunkerFunction"))

print(get_required_fields("Chunker","SemanticChunkerFunction"))