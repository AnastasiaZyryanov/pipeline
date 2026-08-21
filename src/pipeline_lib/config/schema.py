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
          "model": { "type": "string",
                    "description": "Name of the LLM model. For OllamaRunner, use a local model name such as 'gemma3:12b'. For VLLMRunner, use the full Hugging Face model ID, such as 'google/gemma-3-12b-it'" },
          "api_key": { "type": "string",
                      "description": "API key for services that require authentication"},
          "seed": { "type": "integer",
                   "description": "Random seed for reproducibility of LLM outputs. Use a fixed integer to get consistent generations across runs." }
        },
        "required": ["model"]    
      },
      "OllamaRunner": {
        "allOf": [
          { "$ref": "#/$defs/LLMRunnerBase" },
          {
            "type": "object",
            "properties": {
              "type": { "const": "OllamaRunner" }
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
              "gpu": { "type": "string",
                      "description": "GPU device to use" },
              "port": { "type": "string",
                       "description": "Network port for the vLLM server (e.g.'8000', '8001')"}
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
          "language": { "type": "string", "description": "Language for tokenizer (e.g. 'en', 'it')" },
          "max_tokens": {"type": "string", 
                         "description": "Maximum number of tokens allowed in a chunk (default size 450)"}   
        },
        "required": ["type"]
      },
      "SemanticChunker": {
        "type": "object",
        "properties": {
          "type": { "const": "SemanticChunkerFunction" },
          "embedding_model": { "type": "string",
                              "description": "Name of the sentence‑transformer model, e.g.'all-MiniLM-L6-v2' or 'sentence-transformers/all-mpnet-base-v2'" },          
          "percentile": { "type": "number",
                         "description": "Threshold for detecting semantic breakpoints between chunks. Lower values produce more chunks, while higher values produce larger chunks. Typical range: 50-90." },
          "overlap": { "type": "integer",
                      "description": "Number of tokens to overlap between consecutive chunks. Usually set between 0 and 50" },
          "language": { "type": "string", 
                       "description": "Language for tokenizer (e.g. 'en', 'it')" },
          "max_tokens": {"type": "string",
                         "description": "Maximum number of tokens allowed in a chunk (default size 450)"}   
      },
        "required": ["type", "embedding_model", "percentile", "overlap"]
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
            "type": {
                "const": "CleanerWithScript"
            },
            "script": {
                "type": "string",
                "description": "Path to the Python script. Leave empty to use the default script 'scripts/clean.py'."
            },
            "entrypoint": {
                "type": "string",
                "description": "Name of the cleaning function inside the script. Leave empty to use the default function 'clean'."
            }
        },
        "required": ["type"],
        "oneOf": [
              { "not": {"anyOf": [
                          {"required": ["script"]},
                          {"required": ["entrypoint"]}
                      ]
                    }
                },
              {"required": ["script", "entrypoint"]}
          ]        
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
          "system_prompt": { "type": "string",
                            "description": "System instructions for the LLM"},
          "user_template": { "type": "string",
                            "description": "Template for the user prompt sent to the LLM" },
          "max_tokens": { "type": "integer",
                         "description": "Maximum number of tokens to generate in the LLM response" },
          "generated_responses": { "type": "integer",
                                  "description": "Number of responses to generate per chunk (final sentiment is taken like an average of them)" },
          "temperature": {"type": "number",
                          "description": "Sampling temperature (in range from 0 to 2). Higher values increase randomness. If generated_responses > 1, temperature should be > 0 to ensure diversity. Default value 1.0."},
          "runner": { "$ref": "#/$defs/LLMRunner" }
        },
        "required": ["type", "generated_responses", "runner"]        
      },
      "SAwithAttention": {
        "type": "object",
        "properties": {
          "type": { "const": "SAwithAttention" },
          "model": { "type": "string", 
                    "description": "HuggingFace model ID for sentiment classification"}
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
          "system_prompt": { "type": "string",
                            "description": "System instructions for the LLM" },
          "user_template": { "type": "string",
                            "description": "Template for the user prompt sent to the LLM" },
          "max_tokens": { "type": "integer",
                         "description": "Maximum number of tokens to generate in the LLM response" },
          "runner": { "$ref": "#/$defs/LLMRunner" }
        },
        "required": ["type", "runner"]
      },
      "KEwithKeyBERT": {
        "type": "object",
        "properties": {
          "type": { "const": "KEwithKeyBERT" },
          "system_prompt": { "type": "string",
                            "description": "System instructions for the LLM" },
          "user_template": { "type": "string",
                            "description": "Template for the user prompt sent to the LLM." },
          "seed_keywords": { 
              "type": "array",
              "items": {"type": "string"},
              "description": "List of seed keywords used to guide candidate keyword selection"
              },
          "embedding_model": { 
              "type": "object",
              "properties": {
                  "name": {"type": "string",
                           "description": "Name of the sentence‑transformer model, e.g. 'all-MiniLM-L6-v2' or 'sentence-transformers/all-mpnet-base-v2'."},
                  "dtype": {"type": "string", "enum": ["float16", "float32"],
                            "description": "Data type for model weights (float16 uses less GPU memory, float32 is more accurate)"},
                  "device": {"type": "string", "enum": ["cpu", "cuda"],
                             "description": "Device used to run the embedding model. 'cuda' requires a compatible GPU; 'cpu' runs the model on the CPU"}
              },
              "required": ["name"]
            },
          "top_n": { "type": "integer",
                    "description": "Max number of candidate keywords extracted by KeyBERT before LLM refinement. Typical range: 5–20"},
          "keyphrase_size": { "type": "integer",
                             "description": "Max length (in words) of each extracted keyphrase. Usually 1–3"},
          "stopwords": { "type": "string", "description": "Comma‑separated list of stopwords"},
          "min_df": { "type": "integer",
                     "description": "Min number of documents in which a term must appear to be considered as a candidate keyword." },
          "use_maxsum": { "type": "boolean",
                         "description": "Used together with MMR to promote diversity among selected keywords" },
          "use_mmr": { "type": "boolean", "description": "Maximal Marginal Relevance. Used to balance relevance and diversity"},
          "diversity": { "type": "number",
                        "description": "Controls the diversity of keywords selected by MMR. Range of 0–1, where 0 is no diversity and 1 is max diversity" },
          "nr_candidates": { "type": "integer",
                            "description": "Number of candidate keywords considered before filtering. Higher values increase computation but may yield better results. Default: 20." },
          "runner": { "$ref": "#/$defs/LLMRunner" }          
        },
        "required": ["type", "embedding_model", "top_n", "keyphrase_size", "stopwords", "min_df", "runner"]
      },
      "KeywordExtractor": {
        "oneOf": [
          { "$ref": "#/$defs/KEwithLLM" },
          { "$ref": "#/$defs/KEwithKeyBERT" }
        ]
      }
    }
  }