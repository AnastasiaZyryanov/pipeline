class ConfigEditor:
    def __init__(self, state):
        self.state = state

    def set_chunker(self, chunker_cfg):
        self.state.config["Chunker"] = chunker_cfg

    def set_cleaner(self, cleaner_cfg):
        self.state.config["Cleaner"] = cleaner_cfg

    def set_sa(self, sa_cfg):
        self.state.config["SentimentAnalyzer"]=sa_cfg

    def set_ke(self, ke_cfg):
        self.state.config["KeywordExtractor"]=ke_cfg