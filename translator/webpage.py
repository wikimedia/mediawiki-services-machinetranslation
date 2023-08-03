"""Webpage translator - Translates the html content at given webpage URL"""

import logging
import logging.config

import requests

from translator import HTMLTranslator, TranslatorMeta

logging.config.fileConfig("logging.conf")


class WebPageTranslator(HTMLTranslator):
    meta = TranslatorMeta(
        name="WebPageTranslator",
        format="webpage",
        description="Translate the content of a given webpage url",
    )

    def translate(self, url: str) -> str:
        # Get the html content for the given URL
        response = requests.get(url)
        return super().translate(response.text)
