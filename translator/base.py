from __future__ import annotations

import logging
import logging.config
from dataclasses import dataclass
from typing import List, Optional

from translator.models import BaseModel, ModelFactory, ModelNotFoundException
from translator.models.config import ModelConfiguration

logging.config.fileConfig("logging.conf")


@dataclass
class TranslatorMeta:
    name: str
    format: str
    description: str
    character_limit: int = 10000

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"


class TranslatorRegistry(type):
    translators: List[type] = []

    def __init__(cls, name, bases, attrs):
        if name != "BaseTranslator":
            TranslatorRegistry.translators.append(cls)

    @classmethod
    def get_translators(self):
        return self.translators


class BaseTranslator(object, metaclass=TranslatorRegistry):
    meta: Optional[TranslatorMeta] = None

    def __init__(
        self, config: ModelConfiguration, source_lang: str, target_lang: str, model_name: str = None
    ):
        self.config = config
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.model_name = model_name
        self.translation_model = None
        self.init()

    def getModel(self) -> BaseModel:
        return ModelFactory(self.config, self.source_lang, self.target_lang, self.model_name)

    def init(self):
        self.translation_model = self.getModel()
        if not self.translation_model:
            raise ModelNotFoundException
        self.model_name = self.translation_model.MODEL

    def translate(self, text: str) -> str:
        """
        Translates text from source language to target language using a machine translation model.

        Args:
        - text: A string representing the input text to be translated.

        Returns:
        - A string representing the translated text in the target language.
        """
        raise Exception("Not implemented")


class InvalidContentException(Exception):
    "Raised when content is not in expected format"

    pass
