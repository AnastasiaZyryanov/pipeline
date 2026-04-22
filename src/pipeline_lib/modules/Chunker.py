import abc

class Chunker(abc.ABC):
    @abc.abstractmethod
    def run(self): pass

class SentenceChunkerFunction(Chunker):
    def __init__(self, language=None):    
        self.language = language

    def run(self, data):
        print("Run sentence chanker")
        return data

class SemanticChunkerFunction(Chunker):
    def __init__(self, embedding_model, percentile, overlap, sentence_chunker):
        self.embedding_model=embedding_model
        self.percentile=percentile
        self.overlap=overlap
        self.sentence_chunker=sentence_chunker

    def run(self, data):
        print("Run semantic chunker")
        return data