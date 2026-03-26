import abc

class KeywordExtractor(abc.ABC):
        @abc.abstractmethod
        def run(self): pass

class KEwithLLM:
    def _init_(self, runner, prompt=None, max_tokens=None):    
        self.prompt=prompt
        self.max_tokents=max_tokens
        self.runner=runner

    @classmethod
    def run(self):
        print("Run keyword extractor with LLM")

class KEwithKeyBERT:
    def _init_(self, embedding_model, top_n, keyphrase_size, stopwords, min_df, runner, prompt=None, seed_keywords=None, use_maxsum=None, use_mmr=None, diversity=None, nr_candidates=None):
        self.embedding_model=embedding_model
        self.top_n=top_n
        self.keyphrase_size=keyphrase_size
        self.stopwords=stopwords
        self.min_df=min_df
        self.runner=runner
        self.prompt=prompt
        self.seed_keywords=seed_keywords
        self.use_maxsum=use_maxsum
        self.use_mmr=use_mmr
        self.diversity=diversity
        self.nr_candidates=nr_candidates

        
    @classmethod
    def run(self):
        print("Run KEwithKeyBERT")