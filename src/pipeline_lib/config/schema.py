PIPELINE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "http://example.com/pipeline.schema.json",
    "title": "Pipeline",
    "description": "A project pipeline metamodel schema",
    "type": "object",
    "properties": {
      "Chunker": { "$ref": "#/$defs/Chunker" },
      "Cleaner": { "$ref": "#/$defs/Cleaner" },
      "SentimentAnalyzer": { "$ref": "#/$defs/SentimentAnalyzer" },
      "KeywordExtractor": { "$ref": "#/$defs/KeywordExtractor" }
    },
    "required": ["Chunker", "Cleaner", "SentimentAnalyzer", "KeywordExtractor"],
    "$defs": {
      "LLMRunnerBase": {
        "type": "object",
        "properties": {
          "model": { "type": "string" },
          "api_key": { "type": "string" },
          "seed": { "type": "integer" }
        },
        "required": ["model"]    
      },
      "OllamaRunner": {
        "allOf": [
          { "$ref": "#/$defs/LLMRunnerBase" },
          {
            "type": "object",
            "properties": {
              "type": { "const": "OllamaRunner" },
              "gpu": { "type": "string" },
              "port": { "type": "string" }
            },
            "required": ["type"]            
          }
        ]
      },
      "VLLMRunner": {
        "allOf": [
          { "$ref": "#/$defs/LLMRunnerBase" },
          {
            "type": "object",
            "properties": {
              "type": { "const": "VLLMRunner" },
              "gpu": { "type": "string" },
              "port": { "type": "string" }
            },
            "required": ["type"]
          }
        ]
      },
      "LLMRunner": {
        "oneOf": [
          { "$ref": "#/$defs/OllamaRunner" },
          { "$ref": "#/$defs/VLLMRunner" }
        ]
      },
      "SentenceChunker": {
        "type": "object",
        "properties": {
          "type": { "const": "SentenceChunkerFunction" },
          "language": { "type": "string" }
        },
        "required": ["type"]
      },
      "SemanticChunker": {
        "type": "object",
        "properties": {
          "type": { "const": "SemanticChunkerFunction" },
          "embedding_model": { "type": "string" },
          "percentile": { "type": "number" },
          "overlap": { "type": "integer" },
          "sentence_chunker": { "$ref": "#/$defs/SentenceChunker" }
        },
        "required": ["type", "embedding_model", "percentile", "overlap", "sentence_chunker"]
      },
      "Chunker": {
        "oneOf": [
          { "$ref": "#/$defs/SentenceChunker" },
          { "$ref": "#/$defs/SemanticChunker" }
        ]
      },
      "NoClean": {
        "type": "object",
        "properties": {
          "type": { "const": "NoClean" }
        },
        "required": ["type"]
      },
      "CleanerWithScript": {
        "type": "object",
        "properties": {
          "type": { "const": "CleanerWithScript" },
          "script": { "type": "string" },
          "entrypoint": { "type": "string" }
        },
        "required": ["type", "script"]
      },
      "Cleaner": {
        "oneOf": [
          { "$ref": "#/$defs/NoClean" },
          { "$ref": "#/$defs/CleanerWithScript" }
        ]
      },
      "SAwithLLM": {
        "type": "object",
        "properties": {
          "type": { "const": "SAwithLLM" },
          "prompt": { "type": "string" },
          "max_tokens": { "type": "integer" },
          "generated_responses": { "type": "integer" },
          "runner": { "$ref": "#/$defs/LLMRunner" }
        },
        "required": ["type", "generated_responses", "runner"]        
      },
      "SAwithAttention": {
        "type": "object",
        "properties": {
          "type": { "const": "SAwithAttention" },
          "model": { "type": "string" }
        },
        "required": ["type"]
      },
      "SentimentAnalyzer": {
        "oneOf": [
          { "$ref": "#/$defs/SAwithLLM" },
          { "$ref": "#/$defs/SAwithAttention" }
        ]
      },
      "KEwithLLM": {
        "type": "object",
        "properties": {
          "type": { "const": "KEwithLLM" },
          "prompt": { "type": "string" },
          "max_tokens": { "type": "integer" },
          "runner": { "$ref": "#/$defs/LLMRunner" }
        },
        "required": ["type", "runner"]
      },
      "KEwithKeyBERT": {
        "type": "object",
        "properties": {
          "type": { "const": "KEwithKeyBERT" },
          "prompt": { "type": "string" },
          "seed_keywords": { "type": "string" },
          "embedding_model": { "type": "string" },
          "top_n": { "type": "integer" },
          "keyphrase_size": { "type": "integer" },
          "stopwords": { "type": "string" },
          "min_df": { "type": "integer" },
          "use_maxsum": { "type": "boolean" },
          "use_mmr": { "type": "boolean" },
          "diversity": { "type": "number" },
          "nr_candidates": { "type": "integer" },
          "runner": { "$ref": "#/$defs/LLMRunner" }
        },
        "required": ["type", "embedding_model", "top_n", "keyphrase_size", "stopwords", "min_frequency", "runner"]
      },
      "KeywordExtractor": {
        "oneOf": [
          { "$ref": "#/$defs/KEwithLLM" },
          { "$ref": "#/$defs/KEwithKeyBERT" }
        ]
      }
    }
  }