"""SVG translator."""

import logging
import logging.config
from typing import Dict
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from translator import BaseTranslator, TranslatorMeta

logging.config.fileConfig("logging.conf")

# Register common namespaces
namespaces = {
    "": "http://www.w3.org/2000/svg",  # SVG
    "xlink": "http://www.w3.org/1999/xlink",  # XML Linking Language
    "cc": "http://creativecommons.org/ns#",  # Permissions and Licences
    "cdml": "http://www.freesoftware.fsf.org/bkchem/cdml",  # Chemical diagrams
    "dc": "http://purl.org/dc/elements/1.1/",  # Metadata
    "i": "http://ns.adobe.com/AdobeIllustrator/10.0/",  # Adobe Illustrator
    "inkscape": "http://www.inkscape.org/namespaces/inkscape",
    "its": "http://www.w3.org/2005/11/its",  # Internationalization Tag Set
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",  # Resource Description Format
    "serif": "http://www.serif.com/",  # Serif Affinity
    "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd",  # Graphics
}
for prefix in namespaces:
    ElementTree.register_namespace(prefix, namespaces.get(prefix))


class SVGTranslator(BaseTranslator):
    meta = TranslatorMeta(name="SVGTranslator", format="svg", description="Translate svg content")

    def __init__(self, config, source_lang, target_lang, model_name: str = None):
        super().__init__(config, source_lang, target_lang, model_name)
        self.translatables: Dict[str, str] = {}

    def translate(self, svg_str: str) -> str:
        """
        Translates svg from source language to target language using a machine translation model.

        Args:
        - text: A string representing the input text to be translated.

        Returns:
        - Translated svg in string format
        """
        root: Element = ElementTree.fromstring(svg_str)
        self.traverse(root, mode="extract")

        sentences = self.translatables.keys()
        translated_sentences = self.translation_model.translate(
            self.source_lang, self.target_lang, sentences
        )
        self.translatables = dict(zip(sentences, translated_sentences))
        translated_svg = self.traverse(root, mode="apply")
        return ElementTree.tostring(translated_svg, encoding="unicode")

    def traverse(self, root: Element, mode="extract") -> Element:
        extract_mode: bool = mode == "extract"

        text_nodes = [
            *root.iter("{http://www.w3.org/2000/svg}text"),
            *root.iter("{http://www.w3.org/2000/svg}textPath"),
        ]
        for text_node in text_nodes:
            if text_node.text is not None:
                if len(list(text_node)) > 0:
                    continue
                if extract_mode:
                    self.translatables[text_node.text] = text_node.text
                else:
                    text_node.text = self.translatables.get(text_node.text, text_node.text)
        # FIXME: Support tspan - will require fuzzy matching we did in HTML translator.
        # FIXME: https://commons.wikimedia.org/wiki/Help:SVG#systemLanguage_processing
        # See https://upload.wikimedia.org/wikipedia/commons/c/cb/Planets2013.svg
        # and https://upload.wikimedia.org/wikipedia/commons/a/a4/The_Solar_System.svg
        return root
