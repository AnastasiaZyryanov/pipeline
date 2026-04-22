from ..modules.Chunker import * 
from ..modules.Cleaner import * 
from ..modules.SentimentAnalyzer import * 
from ..modules.KeywordExtractor import * 
from ..modules.LLMRunner import * 


def create_module(config):
    match config["type"]:
        case "OllamaRunner":
            return OllamaRunner(gpu=config.get("gpu"), port=config.get("port"))
        case "VLLMRunner":
            return VLLMRunner(gpu=config.get("gpu"), port=config.get("port"))
        case "SentenceChunkerFunction":
            return SentenceChunkerFunction(language=config.get("language"))
        case "SemanticChunkerFunction":
            return SemanticChunkerFunction(embedding_model=config["embedding_model"], percentile=config["percentile"], overlap=config["overlap"], sentence_chunker=config["sentence_chunker"])
        case "NoClean":
            return NoClean()
        case "CleanerWithScript":
            return CleanerWithScript(script=config["script"], entrypoint=config.get("entrypoint"))
        case "SAwithLLM":
            return SAwithLLM(generated_responses=config["generated_responses"], runner=config["runner"], prompt=config.get("prompt"), max_tokens=config.get("max_tokens"))
        case "SAwithAttention":
            return SAwithAttention(model=config.get("model"))
        case "KEwithLLM":
            return KEwithLLM(runner=config["runner"], prompt=config.get("prompt"), max_tokens=config.get("max_tokens"))
        case "KEwithBERT":
            return KEwithKeyBERT(embedding_model=config["embedding_model"], top_n=config["top_n"], keyphrase_size=config["keyphrase_size"], min_df=config["min_df"], runner=config["runner"], prompt=config.get("prompt"), seed_keywords=config.get("seed_keywords"), use_maxsum=config.get("use_maxsum"), use_mmr=config.get("use_mmr"), diversity=config.get("diversity"), nr_candidates=config.get("nr_candidates"))
        case _:
            raise ValueError("Unknown type")