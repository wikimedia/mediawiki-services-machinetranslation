from __future__ import annotations

import logging
import logging.config

from translator.models import BaseModel, ModelFactory, ModelNotFoundException

logging.config.fileConfig("logging.conf")


class BaseTranslator:
    def __init__(self, config, source_lang, target_lang):
        self.config = config
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.translation_model = None
        self.init()

    def getModel(self) -> BaseModel:
        return ModelFactory(self.config, self.source_lang, self.target_lang)

    def init(self):
        self.translation_model = self.getModel()
        if not self.translation_model:
            raise ModelNotFoundException

    def translate(self, text: str) -> str:
        """
        Translates text from source language to target language using a machine translation model.

        Args:
        - text: A string representing the input text to be translated.

        Returns:
        - A string representing the translated text in the target language.
        """
        raise Exception("Not implemented")

    @property
    def model_name(self) -> str:
        return self.translation_model.MODEL


class InvalidContentException(Exception):
    "Raised when content is not in expected format"
    pass
