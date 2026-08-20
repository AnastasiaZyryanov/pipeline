import numpy as np
import nltk
from ..core.module_base import PipelineModule
nltk.download('punkt_tab')

class Chunker(PipelineModule):
    def run(self): pass

    def _split_long_chunk(self, text, max_tokens): 
        # Approximate token estimation:1 token ≈ 0.75 words,  1 word ≈ 1.33 tokens
        # Exact tokenization depends on the model tokenizer. 
        words = text.split()
        estimated_tokens = len(words) * 1.33

        if estimated_tokens <= max_tokens:
            return [text]
        chunk_size_words = int(max_tokens / 1.33)
        if chunk_size_words < 1:
            chunk_size_words = 1
        chunks = []
        for i in range(0, len(words), chunk_size_words):
            chunk = ' '.join(words[i:i+chunk_size_words])
            chunks.append(chunk)
        return chunks

class SentenceChunkerFunction(Chunker):
    def __init__(self, language=None, max_tokens=450):    
        self.language = language
        self.max_tokens = max_tokens 
           
    def run(self, data):
        print("Run sentence chunker")                
        data = data.copy()
        data = data.dropna(subset=["comment"]).reset_index(drop=True)

        data["sentences"] = data["comment"].apply(
            lambda x: nltk.tokenize.sent_tokenize(x, language=self.language)
            if self.language else nltk.tokenize.sent_tokenize(x))
        data["chunk"] = data.apply(
            lambda row: [subchunk for sent in row["sentences"] 
                               for subchunk in self._split_long_chunk(sent, self.max_tokens)], axis=1
        )        
        data['comment'] = data.index      
        data = data.explode('chunk')        
        data.drop_duplicates(subset=['chunk'], inplace=True)

        sentences_lengths = data['chunk'].apply(lambda x: len(nltk.word_tokenize(x)))
        data = data[sentences_lengths > np.percentile(sentences_lengths, 25)].reset_index(drop=True)

        return data
    
from sentence_transformers import SentenceTransformer
    
class SemanticChunkerFunction(Chunker):
    def __init__(self, embedding_model, percentile, overlap, language=None, max_tokens=450):        
        self.embedding_model = SentenceTransformer(embedding_model, trust_remote_code = True)
        self.percentile=percentile
        self.overlap=overlap
        self.language = language
        self.max_tokens = max_tokens

    def run(self, data):
        print("Run semantic chunker")
        data = data.copy()        
        data = data.dropna(subset=["comment"]).reset_index(drop=True) 
        data['sentences'] = data['comment'].astype(str).apply(self.split_text)
        data['combined'] = data['sentences'].apply(lambda x: list(self.combine_sentences(x)))
        data['distances'] = data['combined'].apply(lambda x: list(self.distance_to_next(x, self.embedding_model)))
        breakpoint_threshold = np.nanpercentile(data['distances'].explode().values, 75)
        data['breakpoints'] = data['distances'].apply(lambda x: self.calculate_breakpoints(x, breakpoint_threshold))
        data["comment"] = data.index
        data['chunk'] = data.apply(lambda row: self.create_chunks(row['breakpoints'], row['sentences']), axis=1)
        chunks = data.explode('chunk')[['comment', 'chunk']].reset_index(drop=True)
        return chunks

    def combine_sentences(self, sentences):
        if len(sentences) < 2:
            yield from sentences
            return
        
        yield ' '.join((sentences[0], sentences[1]))

        for i in range(1, len(sentences)-1):
            yield ' '.join(sentences[i-1:i+2])
        
        yield ' '.join((sentences[-2], sentences[-1]))

    def split_text(self, text):      
        sentences = nltk.tokenize.sent_tokenize(text, language=self.language) if self.language else nltk.tokenize.sent_tokenize(text)
        
        return [s.replace('\n', ' ').strip() for s in sentences]


    def distance_to_next(self, sentences, model: SentenceTransformer):
        for couple in zip(sentences, sentences[1:]):
            encodings = model.encode(couple, prompt_name='Clustering')
            yield 1 - model.similarity(encodings[0], encodings[1]).item()
        
        yield np.nan  


    def calculate_breakpoints(self, distances, threshold):
        return [0] + [i for i, d in enumerate(distances, start=1) if d > threshold] + [len(distances)]


    def create_chunks(self, breakpoints, sentences):
        raw_chunks = [
            ' '.join(sentences[start:end])
            for start, end in zip(breakpoints, breakpoints[1:])
        ]

        final_chunks = []
        for chunk in raw_chunks:
            split_chunks = self._split_long_chunk(chunk, self.max_tokens)
            final_chunks.extend(split_chunks)

        return final_chunks