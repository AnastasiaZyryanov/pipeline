import abc

class Chunker(abc.ABC):
    @abc.abstractmethod
    def run(self): pass

class SemanticChunkerFunction:
    def _init_(self, language=None):    
        self.language = language

    @classmethod
    def run(self):
        print("Run semantic chanker")

class SentenceChunkerFuncrion:
    def _init_(self, embedding_model, percentile, overlap, sentence_chunker):
        self.embedding_model=embedding_model
        self.percentile=percentile
        self.overlap=overlap
        self.sentence_chunker=sentence_chunker

    @classmethod
    def run(self):
        print("Run sentence chunker")