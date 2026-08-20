from ..core.module_base import PipelineModule
import numpy as np

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
            label = self.score_to_label(mean_score)
            responses.append(label)                     
                 
        data = data.copy()             
        data["sentiment"] = responses

        return data
    
    def score_to_label(self,score):
        if score <= -1.5:
            return "Very Negative"
        elif score <= -0.5:
            return "Negative"
        elif score < 0.5:
            return "Neutral"
        elif score < 1.5:
            return "Positive"
        else:
            return "Very Positive"
    
    def get_runner(self):
        return self.runner    
    

class SAwithAttention(SentimentAnalyzer):
    def __init__(self, model):
        if model is None:
            model = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.model_name = model   
        from transformers import pipeline
        self.classifier = pipeline(
            "sentiment-analysis",
            model=model,
            truncation=False,            
            max_length = None        
        )
                
    def run(self, data):
        print("Run sentiment analyzer with attention")
        
        data = data.copy()
        documents = data["chunk"].astype(str).tolist()

        max_len = 0
        for i, doc in enumerate(documents):
            n = len(
                self.classifier.tokenizer.encode(
                    doc,
                    add_special_tokens=True
                )
            )
            max_len = max(max_len, n)

            if n > 512:
                print(f"OVERFLOW: chunk {i} -> {n}")

        #print("Max tokens:", max_len)

        results = self.classifier(documents)
        label_map = {
            "negative": "Negative",
            "neutral": "Neutral",
            "positive": "Positive"
        }
        sentiments = [
            label_map.get(r["label"].lower(), r["label"])
            for r in results
        ]
        data["sentiment"] = sentiments
        return data