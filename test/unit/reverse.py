"""A translation model that translates by reversing words in sentences. Used for unit tests"""
import logging
import logging.config
import re
from typing import List

from translator.models import BaseModel

logging.config.fileConfig("logging.conf")


class ReverseTransModel(BaseModel):
    MODEL = "reversetrans"

    def init(self):
        pass

    def translate(self, src_lang: str, tgt_lang: str, sentences: List[str]) -> List[str]:
        """
        Translates text from source language to target language using a machine translation model.

        Args:
        - src_lang: A string representing the source language of the input text.
          Must be a valid language code.
        - tgt_lang: A string representing the target language for the translation output.
          Must be a valid language code.
        - sentences: List of sentences to be translated.

        Returns:
        - List of translated sentences.
        """
        translated_sentences: List[str] = []
        for sentence in sentences:
            words: List[str] = re.split(r"[\s]+", sentence.strip(". "))
            translation = " ".join(words[::-1])
            if "." in sentence:
                translation += "."
            translated_sentences.append(translation)

        return translated_sentences
