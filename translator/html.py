"""HTML translator."""

import logging
import logging.config
import re
from typing import Dict, List, Tuple

from bs4 import BeautifulSoup, NavigableString, PageElement
from Levenshtein import distance

from translator import BaseTranslator, TranslatorMeta
from translator.segmenter import segment

logging.config.fileConfig("logging.conf")

WORD_STOPS = " !\"#$%&'()*+,-./:;<=>?@\\^_`|~"
# Non Translatable tags. Do not traverse through the child nodes of these nodes.
NON_TRANSLATABLE_TAGS = [
    "head",
    "script",
    "style",
    "link",
    "sup",
    "acronym",
    "abbrev",
    "address",
    "area",
    "audio",
    "base",
    "bdi",
    "bdo",
    "br",
    "hr",
    "canvas",
    "code",
    "data",
    "datalist",
    "embed",
    "iframe",
    "img",
    "ins",
    "kbd",
    "meter",
    "noscript",
    "template",
    "slot",
]


def ngram(sentence: str, n: int) -> List[str]:
    """
    Returns a list of n-grams (contiguous sublists of length n) from the sentence.

    Parameters:
    sentence (str): The input sentence
    n (int): The length of the n-grams

    Returns:
    list: The list of n-grams
    """

    # Split the sentence into individual words
    # NOTE: This works only for languages that use space as word seperator
    # For other languages, this method has no effect
    words = sentence.split()

    # Create n-grams by iterating over the words list and selecting sublists of length n
    ngrams = [words[i : i + n] for i in range(len(words) - n + 1)]

    return ngrams


def fuzzy_find(text, key, search_start=0) -> Tuple[int, str]:
    """
    Search for a fuzzy match of a key in a given text.

    Parameters:
        text (str): The text in which to search for the key.
        key (str): The key to search for.
        search_start (int): The index to start the search from in the text. Defaults to 0.

    Returns:
        Tuple[str, int, int]: A tuple containing the matched substring, the start index of the
        fuzzy match and end index of fuzzy match,
        or (None, -1, -1) if no match is found.

    """
    # Quick test
    if key.strip().lower() == text.strip().lower():
        return (key, 0, len(key))

    key = key.strip().lower()
    context = text[search_start:].lower()

    if not len(key):
        # logging.debug(f"Error: Could not locate [{key}] in [{context}]")
        return (None, -1, -1)

    candidates = [key]

    number_of_words_in_key = len(key.split())
    score_cutoff = 3
    # Find all ngrams in the text where n = number_of_words_in_key
    ngram_words: List[str]
    for ngram_words in ngram(context, number_of_words_in_key):
        phrase = " ".join(ngram_words)
        if distance(phrase, key, score_cutoff=score_cutoff) < score_cutoff:
            candidates.append(phrase)

    for candidate in candidates:
        start = search_start + context.find(candidate)
        end = start + len(candidate)
        if start >= 0:
            if end == len(text):
                return (text[start:], start, end)

            for i in range(end, len(text)):
                # Find nearest space or terminators
                if text[i] in WORD_STOPS:
                    selection = text[start:i]
                    return (selection, start, i)

    # print(f"Error: Could not locate [{key}] in [{context}]")
    return (None, -1, -1)


def is_leaf_node(node):
    """
    Check if a given BeautifulSoup node is a leaf node,
    i.e., it does not have any further child nodes.

    Parameters:
    node (Tag or NavigableString): The BeautifulSoup node to check

    Returns:
    bool: True if the node is a leaf node, False otherwise
    """

    # Check if the node only contains a single NavigableString object, indicating it is a leaf node
    if len(node.contents) == 1 and isinstance(node.contents[0], NavigableString):
        return True

    countable_nodes = []
    for child_node in node.contents:
        if child_node.get_text() == "\n":  # Skip newline characters
            continue
        countable_nodes.append(child_node)

    # Check if the remaining countable nodes are all NavigableString objects,
    # indicating it is a leaf node
    if len(countable_nodes) == 1 and isinstance(countable_nodes[0], NavigableString):
        return True

    return False


class HTMLTranslator(BaseTranslator):
    meta = TranslatorMeta(
        name="HTMLTranslator",
        format="html",
        description="Translate html content",
        character_limit=100000,
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
        doc: BeautifulSoup = BeautifulSoup(html, "html.parser")
        if doc.find("body"):
            # If the content is a full webpage with body, just translate body.
            # to skip other parts of page.
            self.translate_node(doc.find("body"))
        else:
            self.translate_node(doc)
        return str(doc)

    def translate_node(self, doc: BeautifulSoup) -> None:
        # Extract all translatables
        self.traverse(doc, mode="extract")
        sentences = list(self.translatables.keys())
        translated_sentences = self.translation_model.batch_translate(
            self.source_lang, self.target_lang, sentences
        )
        self.translatables = dict(zip(sentences, translated_sentences))
        # Now apply the translation on same json object
        self.traverse(doc, mode="apply")

    def traverse(self, doc: BeautifulSoup, mode="extract") -> None:
        extract_mode: bool = mode == "extract"

        if not self.is_translatable(doc):
            return

        # Leaf node
        if is_leaf_node(doc):
            text = doc.get_text()
            if extract_mode:
                self.add_to_translatables(text)
            else:
                doc.string = self.get_translation(text)
            return doc

        text = doc.get_text()
        child_nodes = doc.contents
        # Remove all child nodes that are just new lines.
        child_nodes = [cnode for cnode in child_nodes if cnode.string != "\n"]
        is_wrapper_node = not any(isinstance(cnode, NavigableString) for cnode in child_nodes)

        if extract_mode:
            if not is_wrapper_node:
                self.add_to_translatables(text)
            for node in child_nodes:
                if isinstance(node, NavigableString):
                    continue
                self.traverse(node, mode)
        else:
            if is_wrapper_node or len(child_nodes) == 1:
                # If the node is a wrapper for one or more non-text nodes(example: ul, ol, table),
                # there is no need for fuzzy matching and markup fixing.
                # Same is the case for a simple node with just one text or non-text child
                doc_inner_content = ""
                for cnode in child_nodes:
                    self.traverse(cnode, mode)
                    doc_inner_content += str(cnode)

            else:
                # Mark up fixups
                doc_inner_content: str = self.get_translation(text)
                for node in child_nodes:
                    if isinstance(node, NavigableString):
                        continue

                    search_start = 0
                    self.traverse(node, mode)
                    node_text = node.get_text()
                    node_html = str(node)

                    # Locate node_child_text in node_translation
                    # print("\t", doc.name, ">", node.name, ">", node_text)
                    (match, translation_start, translation_end) = fuzzy_find(
                        doc_inner_content, node_text, search_start=search_start
                    )

                    if translation_start < 0:
                        continue

                    doc_inner_content = "".join(
                        [
                            doc_inner_content[:translation_start],
                            node_html,
                            doc_inner_content[translation_end:],
                        ]
                    )
                    search_start = translation_start + len(node_html)

            doc.clear()
            doc.insert(0, BeautifulSoup(doc_inner_content, "html.parser"))
            # print(doc.name, "===", doc_inner_content)

    def add_to_translatables(self, text: str):
        text = text.strip()
        if len(text) == 0:
            return
        if text in self.translatables:
            return
        if re.sub(r"[^\w]", "", text).isnumeric():
            return
        sentences = segment(self.source_lang, text)
        if len(sentences) == 1:
            self.translatables[sentences[0]] = sentences[0]
        for sentence in sentences:
            self.add_to_translatables(sentence)

    def get_translation(self, text: str) -> str:
        text = text.strip()
        if len(text) == 0:
            return text

        sentences = segment(self.source_lang, text)
        if len(sentences) == 1:
            return self.translatables.get(sentences[0], sentences[0])
        return " ".join([self.get_translation(sentence) for sentence in sentences])

    def is_translatable(self, node: PageElement) -> bool:
        if node.name in NON_TRANSLATABLE_TAGS:
            return False

        classes: List[str] = node.attrs.get("class")
        if classes and "notranslate" in classes:
            return False

        return True
