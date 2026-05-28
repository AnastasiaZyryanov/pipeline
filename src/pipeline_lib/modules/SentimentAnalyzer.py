from transformers import pipeline
from ..core.module_base import PipelineModule
import numpy as np
from ..utils import score_to_label

class SentimentAnalyzer(PipelineModule):
        def run(self): pass

class SAwithLLM(SentimentAnalyzer):
    def __init__(self, generated_responses, runner, system_prompt=None, user_template=None, max_tokens=None, temperature=None):    
        self.system_prompt=system_prompt
        self.user_template=user_template
        self.generated_responses=generated_responses
        self.max_tokens=max_tokens
        self.runner=runner
        self.temperature=temperature
        
    def run(self, data):
        print("Run sentiment analyzer with LLM")

        if self.runner is None:
            raise ValueError("Runner is not initialized")

        documents = data["chunk"].astype(str).tolist()
           
        #if not isinstance(self.generated_responses, int) or self.generated_responses < 1:
        if self.generated_responses<1:
            raise ValueError(f"generated_responses must be a positive integer")
        
        results = self.runner.generate(
                    documents=documents,
                    system_prompt=self.system_prompt,
                    user_template=self.user_template,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    generated_responses=self.generated_responses
                    )
                    
        sentiment_map = {'Very Negative': -2, 'Negative': -1, 'Neutral': 0, 'Positive': 1, 'Very Positive': 2}
        responses = []

        for result in results:
            scores = [sentiment_map.get(choice, np.nan) for choice in result]
            mean_score = np.nanmean(scores)
            label = score_to_label(mean_score)
            responses.append(label)                     
                 
        data = data.copy()             
        data["sentiment"] = responses

        return data
    
    def get_runner(self):
        return self.runner    
    

class SAwithAttention(SentimentAnalyzer):
    def __init__(self, model):
        if model is None:
            model = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.model_name = model

        #distilbert-base-uncased-finetuned-sst-2-english
        #siebert/sentiment-roberta-large-english

        self.classifier = pipeline(
            "sentiment-analysis",
            model=model,
            truncation=True,
            max_length = 512
        )
                
    def run(self, data):
        print("Run sentiment analyzer with attention")
        
        data = data.copy()
        documents = data["chunk"].astype(str).tolist()
        results = self.classifier(documents)

        sentiments = [
            r["label"]
            for r in results
        ]

        data["sentiment"] = sentiments
        #data["sentiment_score"] = [ r["score"] for r in results]

        return data