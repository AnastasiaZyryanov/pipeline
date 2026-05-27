from transformers import pipeline
from collections import Counter
from ..core.module_base import PipelineModule
from ..utils import log_progress

class SentimentAnalyzer(PipelineModule):
        def run(self): pass

class SAwithLLM(SentimentAnalyzer):
    def __init__(self, generated_responses, runner, system_prompt=None, user_template=None, max_tokens=None, temperature=0):    
        self.system_prompt=system_prompt
        self.user_template=user_template
        self.generated_responses=generated_responses
        self.max_tokens=max_tokens
        print(f"[SentimentAnalyzer] __init__ received runner: {runner}")
        self.runner=runner
        self.temperature=temperature

    def run(self, data):
        print("Run sentiment analyzer with LLM")

        if self.runner is None:
            raise ValueError("Runner is not initialized")

        print("RUNNER:", self.runner)
        print("CLIENT:", getattr(self.runner, "client", None))
             
        documents = data["chunk"].astype(str).tolist()

        generated_responses = self.generated_responses
    
        if not isinstance(generated_responses, int) or generated_responses < 1:
            raise ValueError(f"generated_responses must be a positive integer")
        
        results = self.runner.generate(
                    documents=documents,
                    system_prompt=self.system_prompt,
                    user_template=self.user_template,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    generated_responses=generated_responses
                    )
            # self.pipeline.stats["chunks_processed"] += 1

            # if self.pipeline.stats["chunks_processed"] % 50 == 0:
            #         log_progress(self.pipeline)
            
        data = data.copy()             
        data["sentiment"] = results

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