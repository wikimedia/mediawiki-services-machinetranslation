"""HTML translator."""

import logging
import logging.config
from typing import Dict, List, Tuple

from bs4 import BeautifulSoup

from translator import BaseTranslator, TranslatorMeta
from translator.segmenter import segment

logging.config.fileConfig("logging.conf")

WORD_STOPS = " !\"#$%&'()*+,-./:;<=>?@\\^_`|~"


def fuzzy_find(text, key, search_start=0) -> Tuple[int, str]:
    """
    Search for a fuzzy match of a key in a given text.

    Parameters:
        text (str): The text in which to search for the key.
        key (str): The key to search for.
        search_start (int): The index to start the search from in the text. Defaults to 0.

    Returns:
        Tuple[int, str]: A tuple containing the start index of the
        fuzzy match and the matched substring,
        or (-1, None) if no match is found.

    """

    key = key.strip()
    context = text[search_start:]
    if not len(key):
        return (-1, None)

    candidates = [
        key,  # Exact match
        key.lower(),  # Lower case
        key[0].lower() + key[1:],  # lower case the first letter and the rest
        key[:-1],  # Suffix inflection at last letter
        key[:-2],  # Suffix inflection at last two letters
    ]

    for candidate in candidates:
        start = search_start + context.find(candidate)
        end = start + len(candidate)
        if start >= 0:
            for i in range(end, len(text)):
                # Find nearest space or terminators
                if text[i] in WORD_STOPS:
                    selection = text[start:i]
                    return (start, selection)

    return (-1, None)


class HTMLTranslator(BaseTranslator):
    meta = TranslatorMeta(
        name="HTMLTranslator", format="html", description="Translate html content"
    )

    def __init__(self, config, source_lang, target_lang):
        super().__init__(config, source_lang, target_lang)
        self.translatables: Dict[str, str] = {}
        # Keep all paragraph text mapped to sentences in it.
        self.paragraphs: Dict[str, List[str]] = {}

    def translate(self, html: str) -> str:
        """
        Translates json from source language to target language using a machine translation model.

        Args:
        - text: A string representing the input text to be translated.

        Returns:
        - Translated Json in string format
        """

        # Extract all translatables
        doc: BeautifulSoup = BeautifulSoup(html, "html.parser")
        self.traverse(doc, mode="extract")
        sentences = list(self.translatables.keys())
        # sentences = sentences[0:100]
        # [print(sentence) for sentence in sentences]
        translated_sentences = self.translation_model.batch_translate(
            self.source_lang, self.target_lang, sentences
        )
        self.translatables = dict(zip(sentences, translated_sentences))
        # Now apply the translation on same json object
        translated_doc = self.traverse(doc, mode="apply")
        return str(translated_doc)

    def traverse(self, doc: BeautifulSoup, mode="extract"):
        extract_mode: bool = mode == "extract"
        inline_tags = "a, b, strong, i, u, sup, mark, span, small, em, td"
        # apply_mode: bool = mode == "apply"
        for heading in doc.css.select("h1, h2, h3, h4, h5, h6"):
            text = heading.get_text()
            if extract_mode:
                self.translatables[text] = text
            else:
                heading.string = self.get_translation(text)

        for block in doc.css.select("p, li, option, label"):
            text = block.get_text()
            sentences = segment(self.source_lang, text)
            p_children = block.css.select(inline_tags)
            if extract_mode:
                [self.add_to_translatables(sentence) for sentence in sentences]
            else:
                p_translation: str = " ".join(
                    [self.get_translation(sentence) for sentence in sentences]
                )
                for p_child in p_children:
                    search_start = 0
                    p_child_text = p_child.get_text()
                    # Locate its translation in paragraph_translation
                    p_child_translation = self.get_translation(p_child_text)

                    if not len(p_child_translation):
                        continue

                    (p_child_translation_start, match) = fuzzy_find(
                        p_translation, p_child_translation, search_start=search_start
                    )

                    if p_child_translation_start >= search_start:
                        p_child_translation_end = p_child_translation_start + len(match)
                        p_child.string = match
                        p_translation = "".join(
                            [
                                p_translation[:p_child_translation_start],
                                str(p_child),
                                p_translation[p_child_translation_end:],
                            ]
                        )
                        search_start = p_child_translation_start + len(str(p_child))
                    # else:
                    #     print(p_child_translation)
                block.clear()
                block.insert(0, BeautifulSoup(p_translation, "html.parser"))

        for tag in doc.css.select(inline_tags):
            # FIXME: What will happen if the link applies
            # to a long paragraph with multiple sentences?
            if len(list(tag.children)) > 1:
                continue
            text = tag.get_text()
            if extract_mode:
                self.add_to_translatables(text)
            else:
                tag.string = self.get_translation(text)

        return doc

    def add_to_translatables(self, text: str):
        text = text.strip()
        if len(text) == 0:
            return
        if text in self.translatables:
            return
        if text.isnumeric():
            return
        self.translatables[text] = text

    def get_translation(self, text: str) -> str:
        key = text.strip()
        if len(text) == 0:
            return text
        return self.translatables.get(key, text)
