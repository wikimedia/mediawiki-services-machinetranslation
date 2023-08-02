import yaml


class ModelConfig:
    def __init__(self):
        self.models = None
        self.config = None
        self.language_pair_mapping = {}
        self.init()

    def init(self):
        with open("./models.yaml") as f:
            self.models = yaml.load(f, Loader=yaml.SafeLoader)
        with open("./config.yaml") as f:
            self.config = yaml.load(f, Loader=yaml.SafeLoader)

        for model in self.config["models"]:
            languages = self.config["models"][model]
            for lang1 in languages:
                for lang2 in languages:
                    if lang1 != lang2:
                        if lang1 not in self.language_pair_mapping:
                            self.language_pair_mapping[lang1] = {}
                        self.language_pair_mapping[lang1][lang2] = model

        for src in self.config["languages"]:
            for target in self.config["languages"][src]:
                if src not in self.language_pair_mapping:
                    self.language_pair_mapping[src] = {}
                self.language_pair_mapping[src].update(target)

    def get_all_languages(self):
        return self.language_pair_mapping
