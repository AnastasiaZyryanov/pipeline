import abc
from transformers import pipeline
from collections import Counter

class SentimentAnalyzer(abc.ABC):
        @abc.abstractmethod
        def run(self): pass

class SAwithLLM(SentimentAnalyzer):
    def __init__(self, generated_responses, runner, system_prompt=None, user_template=None, max_tokens=None, temperature=0):    
        self.system_prompt=system_prompt
        self.user_template=user_template
        self.generated_responses=generated_responses
        self.max_tokens=max_tokens
        self.runner=runner
        self.temperature=temperature

    def run(self, data):
        print("Run sentiment analyzer with LLM")
             
        documents = data["chunk"].astype(str).tolist()

        n = self.generated_responses
    
        if not isinstance(n, int) or n < 1:
            raise ValueError(f"generated_responses must be a positive integer")
        
        results = []
        for doc in documents:
            responses = []
            for _ in range(n):
                resp = self.runner.generate(
                    documents=[doc],
                    system_prompt=self.system_prompt,
                    user_template=self.user_template,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                    )[0]
                responses.append(resp)
                most_common = Counter(responses).most_common(1)[0][0]
                results.append(most_common)
            
        data = data.copy()             
        data["sentiment"] = results

        return data

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
            truncation=True
           # max_length=512 #will loose some information
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