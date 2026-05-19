import abc
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import nltk

class Chunker(abc.ABC):
    @abc.abstractmethod
    def run(self): pass

class SentenceChunkerFunction(Chunker):
    def __init__(self, language=None):    
        self.language = language
        
    def run(self, data):
        print("Run sentence chunker")        
        
        data = data.copy()
        data = data.dropna(subset=["comment"]).reset_index(drop=True)

        data["chunk"] = data["comment"].apply(
            lambda x: nltk.tokenize.sent_tokenize(x)
        )
        
        data['comment'] = data.index      
        data = data.explode('chunk')        
        data.drop_duplicates(subset=['chunk'], inplace=True)

        sentences_lengths = data['chunk'].apply(lambda x: len(nltk.word_tokenize(x)))
        data = data[sentences_lengths > np.percentile(sentences_lengths, 25)].reset_index(drop=True)

        return data
    
class SemanticChunkerFunction(Chunker):
    def __init__(self, embedding_model, percentile, overlap):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.percentile=percentile
        self.overlap=overlap
        #self.sentence_chunker=sentence_chunker
        
    def run(self, data):
        print("Run semantic chunker")

        data = data.copy()        
        data = data.dropna(subset=["comment"]).reset_index(drop=True) 

        data["chunk"] = data["comment"].apply(
            lambda x: nltk.tokenize.sent_tokenize(x)
        )

        data["comment"] = data.index

        semantic_chunks = []

        # process each document separately
        for idx, row in data.iterrows():
            sentences = row["chunk"]
            # skip empty docs
            if not sentences or len(sentences) == 0:
                continue

            # single sentence = single chunk
            if len(sentences) == 1:
                semantic_chunks.append({
                    "comment": row["comment"],
                    "chunk": sentences[0]
                })
                continue

            # embeddings for each sentence
            embeddings = self.embedding_model.encode(sentences)

            similarities = []

            for i in range(len(embeddings) - 1):
                sim = cosine_similarity(
                    [embeddings[i]],
                    [embeddings[i + 1]]
                )[0][0]
                similarities.append(sim)

            threshold = np.percentile(
                similarities,
                self.percentile
            )

            chunks = []
            current_chunk = [sentences[0]]

            for i in range(1, len(sentences)):
                # semantic boundary
                if similarities[i - 1] < threshold:
                    chunks.append(" ".join(current_chunk))

                    overlap_sentences = (
                        current_chunk[-self.overlap:]
                        if self.overlap > 0
                        else []
                    )
                    current_chunk = overlap_sentences + [sentences[i]]
                else:
                    current_chunk.append(sentences[i])

            chunks.append(" ".join(current_chunk))

            for chunk in chunks:
                semantic_chunks.append({
                    "comment": row["comment"],
                    "chunk": chunk
                })

        return pd.DataFrame(semantic_chunks)        