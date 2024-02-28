"""A translation model that translates by reversing words in sentences. Used for unit tests"""
import logging
import logging.config
import re
from typing import Dict, List

from translator.models import BaseModel
from translator.models.utils import apply_missing_references, extract_potential_references

logging.config.fileConfig("logging.conf")


class ReverseTransModel(BaseModel):
    """
    This is a dummy translation model for testing purpose.
    It reverses the words order in the given sentence. The final period(.)
    is kept at the end though.

    This is also a naughty translation model. It can insert spurious references,
    It can remove references present in the source content.

    This simulates the raw MT capability of NMT models.
    The pre, postprocessing steps in the translators should fix this behavior
    and that is what being tested.
    """

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
        reference_map: Dict[str, List[str]] = {}
        for sentence in sentences:
            reference_map[sentence] = extract_potential_references(sentence)

        for sentence in sentences:
            words: List[str] = re.split(r"([\s]+)", sentence.strip(". "))
            # Note: the paranthesis in above regex keep the delimiters as part of splits.
            words = list(
                filter(
                    lambda word: not bool(re.match(r"(\[\s*[0-9a-z]{,3}\s*\])", sentence)), words
                )
            )
            # Add a spurious reference
            words.insert(2, "[123]")
            translation = "".join(words[::-1])
            if "." in sentence:
                translation += "."
            translated_sentences.append(translation)

        translated_sentences = apply_missing_references(reference_map, translated_sentences)

        return translated_sentences
