"""Plain text document translator."""

import logging
import logging.config
from typing import List

from translator import BaseTranslator
from translator.segmenter import segment

logging.config.fileConfig("logging.conf")


class PlainTextTranslator(BaseTranslator):
    def translate(self, text: str) -> str:
        """
        Translates text from source language to target language using a machine translation model.

        Args:
        - text: A string representing the input text to be translated.

        Returns:
        - A string representing the translated text in the target language.
        """
        sentences: List[str] = segment(self.source_lang, text)

        translated_sentences = self.translation_model.translate(
            self.source_lang, self.target_lang, sentences
        )

        return self.compose_text(sentences, translated_sentences)

    def compose_text(
        self,
        sentences: List[str],
        translated_sentences: List[str],
    ) -> str:
        """
        Composes translated text by joining its sentences.

        Args:
        - sentences: A list of strings which represent the original sentences of the text.
        - translated_sentences: A list of strings which represent the machine-translated
          sentences of the text.

        Returns:
        - A single string that represents the translated text by joining
          individual translated sentences.
        """
        translation: str = ""
        for index, sentence in enumerate(translated_sentences):
            if sentences[index] == "\n":
                translation += sentences[index]
            else:
                translation += sentence + " "

        return translation.strip()
