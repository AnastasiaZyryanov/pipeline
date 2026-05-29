from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from keybert.llm import OpenAI
from keybert import KeyBERT, KeyLLM
from sentence_transformers import SentenceTransformer
import torch
from ..core.module_base import PipelineModule

class KeywordExtractor(PipelineModule):
        def run(self): pass

class KEwithLLM(KeywordExtractor):
    def __init__(self, runner, system_prompt=None, user_template=None, max_tokens=None):    
        self.system_prompt=system_prompt
        self.user_template=user_template
        self.max_tokens=max_tokens
        self.runner=runner

    def run(self, data):
        print("Run keyword extractor with LLM")   

        if self.runner is None:
            raise ValueError("Runner is not initialized")

        documents = data["chunk"].astype(str).tolist()
        
        results = list(self.runner.generate(
            documents=documents,
            system_prompt=self.system_prompt,
            user_template=self.user_template,
            max_tokens=self.max_tokens
        ))

        data = data.copy()             
        data["keywords"] = results
        return data    
    
    def get_runner(self):
        return self.runner
          
class KEwithKeyBERT(KeywordExtractor):
    def __init__(self, runner,  embedding_model, top_n, keyphrase_size, stopwords, min_df, system_prompt=None, user_template=None, seed_keywords=None, 
                 use_maxsum=None, use_mmr=None, diversity=0.5, nr_candidates=20):
        model_name = embedding_model["name"]
        dtype_str = embedding_model.get("dtype", "float32")
        dtype = torch.float16 if dtype_str == "float16" else torch.float32
        device = embedding_model.get("device", "cuda")
        self.embedding_model = SentenceTransformer(model_name,model_kwargs={"dtype": dtype}, device=device)
        self.kw_model = KeyBERT(model=self.embedding_model)
        self.top_n=top_n
        self.keyphrase_size=keyphrase_size
        self.stopwords=stopwords
        self.min_df=min_df        
        self.system_prompt=system_prompt
        self.user_template=user_template
        if isinstance(seed_keywords, str):
            self.seed_keywords = seed_keywords.split(", ")
        else:
            self.seed_keywords = seed_keywords
        self.use_maxsum=use_maxsum
        self.use_mmr=use_mmr
        self.diversity=diversity
        self.nr_candidates=nr_candidates             
        self.runner=runner
       
    def run(self, data):
        print("Run keyword extractor with KeyBERT")
        data = data.copy()

        documents = data["chunk"].astype(str).tolist()

        candidates = self.kw_model.extract_keywords(
            documents,
            top_n=self.top_n,
            keyphrase_ngram_range=(1, self.keyphrase_size),
            stop_words=self.stopwords,
            seed_keywords=self.seed_keywords,
            min_df=self.min_df,
            use_maxsum=self.use_maxsum,
            use_mmr=self.use_mmr,
            diversity=self.diversity,
            nr_candidates=self.nr_candidates
    )        
        
        llm_inputs = []

        for doc, cand_list in zip(documents, candidates):
            candidate_keywords = ", ".join(kw[0] for kw in cand_list)
            llm_inputs.append({
                "document": doc,
                "candidates": candidate_keywords
            })
            
        responses = self.runner.generate(
            documents=llm_inputs,
            system_prompt=self.system_prompt,
            user_template=self.user_template,
            max_tokens=None
        )
        all_keywords = []

        for response in responses:                            
            if response is None:
                all_keywords.append([])
                continue
            if isinstance(response, str):
                keywords = response.split(",")
            elif isinstance(response, list):
                keywords = response
            else:
                keywords = []
            keywords = [
                kw.strip().upper()
                for kw in keywords
                if kw and kw.strip()
            ]
            keywords = list(dict.fromkeys(keywords))
            all_keywords.append(keywords)

        data["keywords"] = all_keywords

        return data