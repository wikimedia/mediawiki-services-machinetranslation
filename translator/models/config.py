from typing import Dict, List

import yaml
from pydantic import BaseModel, RootModel


class MTModel(BaseModel):
    model: str
    tokenizer: str


class MTModelConfig(RootModel):
    root: Dict[str, MTModel]

    def get(self, item):
        return self.root[item]

    def keys(self):
        return self.root.keys()


class ModelConfiguration:
    def __init__(self):
        self.models: MTModelConfig = None
        self.config = None
        self.language_pair_mapping = {}
        self.init()

    def init(self):
        with open("./models.yaml") as f:
            self.models = MTModelConfig.model_validate(yaml.load(f, Loader=yaml.SafeLoader))

        with open("./config.yaml") as f:
            self.config = yaml.load(f, Loader=yaml.SafeLoader)

        for model_name in self.config["models"]:
            languages = self.config["models"][model_name]
            for lang1 in languages:
                for lang2 in languages:
                    if lang1 != lang2:
                        if lang1 not in self.language_pair_mapping:
                            self.language_pair_mapping[lang1] = {}
                        elif lang2 in self.language_pair_mapping[lang1]:
                            self.language_pair_mapping[lang1][lang2].append(model_name)
                        else:
                            self.language_pair_mapping[lang1][lang2] = [model_name]

        for src in self.config["languages"]:
            target_languages = self.config["languages"][src]
            for tgt_mapping in target_languages:
                tgt, model_name = next(iter(tgt_mapping.items()))
                if src not in self.language_pair_mapping:
                    self.language_pair_mapping[src] = {}
                elif tgt in self.language_pair_mapping[src]:
                    self.language_pair_mapping[src][tgt].append(model_name)
                else:
                    self.language_pair_mapping[src][tgt] = [model_name]

    def get_all_languages(self):
        return self.language_pair_mapping

    def get_model_names(self) -> List[str]:
        return self.models.keys()

    def is_language_pair_supported(self, source_language, target_language) -> bool:
        """
        Determines if a given language pair is supported by the language pair mapping.

        Parameters:
            source_language (str): The source language.
            target_language (str): The target language.

        Returns:
            bool: True if the language pair is supported, False otherwise.

        """
        return (
            source_language in self.language_pair_mapping
            and target_language in self.language_pair_mapping.get(source_language)
        )
