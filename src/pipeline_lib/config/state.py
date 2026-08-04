from .validator import validate_config

class ConfigurationState:
    def __init__(self, config=None):
        self.config = config or {
            "Chunker": None,
            "Cleaner": None,
            "SentimentAnalyzer": None,
            "KeywordExtractor": None
        }

    def validate(self):
        return validate_config(self.config)