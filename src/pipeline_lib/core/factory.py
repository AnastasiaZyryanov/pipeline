from pipeline_lib.modules.Chunker import SentenceChunkerFunction, SemanticChunkerFunction
from pipeline_lib.modules.Cleaner import CleanerWithScript, NoClean
from pipeline_lib.modules.SentimentAnalyzer import SAwithLLM, SAwithAttention
from pipeline_lib.modules.KeywordExtractor import KEwithLLM, KEwithKeyBERT 
from pipeline_lib.modules.LLMRunner import OllamaRunner, VLLMRunner

MODULE_REGISTRY = {
    "OllamaRunner": lambda cfg: (
        OllamaRunner(
            model=cfg["model"],
            api_key=cfg.get("api_key"),
            seed=cfg.get("seed"),           
            )
    ),    
    "VLLMRunner": lambda cfg: (
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
        language=cfg.get("language"),
        max_tokens=cfg.get("max_tokens", 350)
    ),
    "NoClean": lambda cfg: NoClean(),
    "CleanerWithScript": lambda cfg: CleanerWithScript(
        script=cfg.get("script", "script/clean.py"),
        entrypoint=cfg.get("entrypoint", "clean")
    ),
     "SAwithAttention": lambda cfg: SAwithAttention(
        model=cfg.get("model")
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
            temperature=config.get("temperature"),
        )
    if module_type == "KEwithLLM":
        runner = create_module(config["runner"])
        return KEwithLLM(
            runner=runner,
            system_prompt=config.get("system_prompt"),
            user_template=config.get("user_template"),
            max_tokens=config.get("max_tokens"),
        )
    if module_type == "KEwithKeyBERT":
       runner = create_module(config["runner"])
       return KEwithKeyBERT(      
            runner=runner,   
            embedding_model=config["embedding_model"],
            top_n=config["top_n"],
            keyphrase_size=config["keyphrase_size"],
            stopwords=config["stopwords"], 
            min_df=config["min_df"],
            system_prompt=config.get("system_prompt"),
            user_template=config.get("user_template"),
            seed_keywords=config.get("seed_keywords"),
            use_maxsum=config.get("use_maxsum"),
            use_mmr=config.get("use_mmr"),
            diversity=config.get("diversity"),
            nr_candidates=config.get("nr_candidates", 20),
     )       
    if module_type in MODULE_REGISTRY:
        return MODULE_REGISTRY[module_type](config)

    raise ValueError(f"Unknown type: {module_type}")