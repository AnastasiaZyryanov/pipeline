import abc
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import nltk
from ..utils import split_long_chunk

class Chunker(abc.ABC):
    @abc.abstractmethod
    def run(self): pass

class SentenceChunkerFunction(Chunker):
    def __init__(self, language=None, max_tokens=350):    
        self.language = language
        self.max_tokens = max_tokens 
        
    def run(self, data):
        print("Run sentence chunker")                
        data = data.copy()
        data = data.dropna(subset=["comment"]).reset_index(drop=True)

        data["chunk"] = data["comment"].apply(
            lambda x: nltk.tokenize.sent_tokenize(x)
        )
        #prevent too long chunks
        data["chunk"] = data["chunk"].apply(
            lambda sentences: [subchunk for sent in sentences 
                               for subchunk in split_long_chunk(sent, self.max_tokens)]
        )
        
        data['comment'] = data.index      
        data = data.explode('chunk')        
        data.drop_duplicates(subset=['chunk'], inplace=True)

        sentences_lengths = data['chunk'].apply(lambda x: len(nltk.word_tokenize(x)))
        data = data[sentences_lengths > np.percentile(sentences_lengths, 25)].reset_index(drop=True)

        return data
    
class SemanticChunkerFunction(Chunker):
    def __init__(self, embedding_model, percentile, overlap, max_tokens=350):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.percentile=percentile
        self.overlap=overlap
        self.max_tokens = max_tokens
                
    def run(self, data):
        print("Run semantic chunker")
        data = data.copy()        
        data = data.dropna(subset=["comment"]).reset_index(drop=True) 

        data["chunk"] = data["comment"].apply(lambda x: nltk.tokenize.sent_tokenize(x))
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
                #prevent forming too long chunks
                for sub in split_long_chunk(sentences[0], self.max_tokens):
                    semantic_chunks.append({"comment": row["comment"], "chunk": sub})
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
            raw_chunks = []
            current_chunk = [sentences[0]]

            for i in range(1, len(sentences)):
                # semantic boundary
                if similarities[i - 1] < threshold:
                    raw_chunks.append(" ".join(current_chunk))
                    overlap_sentences = current_chunk[-self.overlap:] if self.overlap > 0 else []
                    current_chunk = overlap_sentences + [sentences[i]]
                else:
                    current_chunk.append(sentences[i])

            if current_chunk:
                raw_chunks.append(" ".join(current_chunk))

            for raw_chunk in raw_chunks:
                for sub in split_long_chunk(raw_chunk, self.max_tokens):
                    semantic_chunks.append({"comment": row["comment"], "chunk": sub})

        return pd.DataFrame(semantic_chunks)      