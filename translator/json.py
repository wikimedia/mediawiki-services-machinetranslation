"""Json translator."""

import json
import logging
import logging.config
from typing import Dict

from translator import BaseTranslator, InvalidContentException, TranslatorMeta

logging.config.fileConfig("logging.conf")


class JSONTranslator(BaseTranslator):
    meta = TranslatorMeta(
        name="JSONTranslator", format="json", description="Translate json content"
    )

    def __init__(self, config, source_lang, target_lang):
        super().__init__(config, source_lang, target_lang)
        self.translatables: Dict[str, str] = {}

    def translate(self, json_str: str) -> str:
        """
        Translates json from source language to target language using a machine translation model.

        Args:
        - text: A string representing the input text to be translated.

        Returns:
        - Translated Json in string format
        """
        try:
            json_obj = json.loads(json_str)
        except Exception as exc:
            raise InvalidContentException from exc

        return self.translate_json_obj(json_obj)

    def translate_json_obj(self, json_obj: any) -> str:
        # Extract all translatables
        self.traverse(json_obj, mode="extract")
        sentences = self.translatables.keys()
        translated_sentences = self.translation_model.translate(
            self.source_lang, self.target_lang, sentences
        )
        self.translatables = dict(zip(sentences, translated_sentences))
        # Now apply the translation on same json object
        translated_obj = self.traverse(json_obj, mode="apply")
        return json.dumps(translated_obj, indent=2, ensure_ascii=False)

    def traverse(self, json_obj, mode="extract"):
        """
        Recursively traverses a JSON object and performs different operations based
        on the type of data encountered.

        Parameters:
        - json_obj : JSON object
            The JSON object to traverse.
        - mode : str, optional (default="extract")
            The mode of operation. "extract" mode adds translatable strings to the `translatables`
            dict, while "apply" mode applies the translated string from the `translatables`
            dictionary.

        Returns:
        - JSON object
            The transformed JSON object.
        """

        if isinstance(json_obj, list):
            # If json_obj is a list, recursively call traverse on each element and return
            # a new list with the results
            return [self.traverse(value, mode) for value in json_obj]
        elif isinstance(json_obj, dict):
            # If json_obj is a dictionary, iterate through each key-value pair
            # Recursively call traverse on the value
            # Return a new dictionary with the original keys and respective values
            return {key: self.traverse(value, mode) for key, value in json_obj.items()}
        elif isinstance(json_obj, str):
            if json_obj.isnumeric():
                # If json_obj is a string and it is numeric, return the string as is
                # We are not translating numerals
                return json_obj
            if mode == "extract":
                # If mode is set to "extract", add the string to the `translatables` dictionary
                # with itself as the value
                self.translatables[json_obj] = json_obj
            if mode == "apply":
                # If mode is set to "apply", retrieve the value from the `translatables` dictionary
                # based on the string
                json_obj = self.translatables.get(json_obj)
            return json_obj
        else:
            # If json_obj is any other type (e.g. int, float, bool), return it as is
            return json_obj
