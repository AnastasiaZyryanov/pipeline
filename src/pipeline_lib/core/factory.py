from pipeline_lib.modules.Chunker import * 
from pipeline_lib.modules.Cleaner import * 
from pipeline_lib.modules.SentimentAnalyzer import *
from pipeline_lib.modules.KeywordExtractor import * 
from pipeline_lib.modules.LLMRunner import * 

MODULE_REGISTRY = {
    "OllamaRunner": lambda cfg: (
        print("Creating OllamaRunner") or
        OllamaRunner(
            model=cfg["model"],
            api_key=cfg.get("api_key"),
            seed=cfg.get("seed"),
           # gpu=cfg.get("gpu"),
           # port=cfg.get("port"),
            )
    ),    
    "VLLMRunner": lambda cfg: (
        print("Creating VLLMRunner") or
        VLLMRunner(
            model=cfg["model"],
            api_key=cfg.get("api_key"),
            seed=cfg.get("seed"),
            gpu=cfg.get("gpu"),
            port=cfg.get("port"),
            )
    ),
    "SentenceChunkerFunction": lambda cfg: SentenceChunkerFunction(
        language=cfg.get("language"),
        max_tokens=cfg.get("max_tokens", 350)        
    ),
    "SemanticChunkerFunction": lambda cfg: SemanticChunkerFunction(
        embedding_model=cfg["embedding_model"],
        percentile=cfg["percentile"],
        overlap=cfg["overlap"],
        max_tokens=cfg.get("max_tokens", 350)
        #sentence_chunker=sentence_chunker,
    ),
    "NoClean": lambda cfg: NoClean(),
    "CleanerWithScript": lambda cfg: CleanerWithScript(
        script=cfg["script"],
        entrypoint=cfg["entrypoint"],
    ),
     "SAwithAttention": lambda cfg: SAwithAttention(
        model=cfg.get("model")
     ),
     "KEwithKeyBERT": lambda cfg: KEwithKeyBERT(         
        embedding_model=cfg["embedding_model"],
        top_n=cfg["top_n"],
        keyphrase_size=cfg["keyphrase_size"],
        stopwords=cfg["stopwords"], 
        min_df=cfg["min_df"],
        system_prompt=cfg.get("system_prompt"),
        user_template=cfg.get("user_template"),
        seed_keywords=cfg.get("seed_keywords"),
        use_maxsum=cfg.get("use_maxsum"),
        use_mmr=cfg.get("use_mmr"),
        diversity=cfg.get("diversity"),
        nr_candidates=cfg.get("nr_candidates"),
     )   
}

def create_module(config):
    module_type = config["type"]
    if module_type == "SAwithLLM":
        runner = create_module(config["runner"])
        return SAwithLLM(
            generated_responses=config["generated_responses"],
            runner=runner,
            system_prompt=config.get("system_prompt"),
            user_template=config.get("user_template"),
            max_tokens=config.get("max_tokens"),
        )
    if module_type == "KEwithLLM":
        runner = create_module(config["runner"])
        return KEwithLLM(
            runner=runner,
            system_prompt=config.get("system_prompt"),
            user_template=config.get("user_template"),
            max_tokens=config.get("max_tokens"),
        )
     
    if module_type in MODULE_REGISTRY:
        return MODULE_REGISTRY[module_type](config)

    raise ValueError(f"Unknown type: {module_type}")