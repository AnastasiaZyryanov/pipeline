import abc
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

class KeywordExtractor(abc.ABC):
        @abc.abstractmethod
        def run(self): pass

class KEwithLLM(KeywordExtractor):
    def __init__(self, runner, system_prompt=None, user_template=None, max_tokens=None):    
        self.system_prompt=system_prompt
        self.user_template=user_template
        self.max_tokents=max_tokens
        self.runner=runner

    def run(self, data):
        print("Run keyword extractor with LLM")        
        documents = data["chunk"].astype(str).tolist()
        
        results = self.runner.generate(
            documents=documents,
            system_prompt=self.system_prompt,
            user_template=self.user_template,
            max_tokens=self.max_tokens
        )
        data = data.copy()             
        data["keyword"] = results
        return data    
          
class KEwithKeyBERT(KeywordExtractor):
    def __init__(self, embedding_model, top_n, keyphrase_size, stopwords, min_df, system_prompt=None, user_template=None, seed_keywords=None, 
                 use_maxsum=None, use_mmr=None, diversity=0.5, nr_candidates=20):
        
        self.embedding_model = SentenceTransformer(embedding_model)
        self.kw_model = KeyBERT(model=self.embedding_model)
        self.top_n=top_n
        self.keyphrase_size=keyphrase_size
        self.stopwords=stopwords
        self.min_df=min_df        
        self.system_prompt=system_prompt
        self.user_template=user_template
        self.seed_keywords=seed_keywords
        self.use_maxsum=use_maxsum
        self.use_mmr=use_mmr
        self.diversity=diversity
        self.nr_candidates=nr_candidates
       
        
    def run(self, data):
        print("Run keyword extractor with KeyBERT")
        data = data.copy()

        documents = data["chunk"].astype(str).tolist()

        all_keywords = []

        for doc in documents:
            keywords = self.kw_model.extract_keywords(doc, keyphrase_ngram_range=(1,self.keyphrase_size),stop_words=self.stopwords,top_n=self.top_n,
                use_maxsum=self.use_maxsum, use_mmr=self.use_mmr, diversity=self.diversity, nr_candidates=self.nr_candidates,seed_keywords=self.seed_keywords)

            keywords = [
                kw[0]
                for kw in keywords
            ]

            all_keywords.append(keywords)

        data["keyword"] = all_keywords

        return data