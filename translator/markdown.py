"""HTML translator."""

import logging
import logging.config

import markdown
from markdownify import markdownify

from translator import HTMLTranslator, TranslatorMeta

logging.config.fileConfig("logging.conf")


class MarkdownTranslator(HTMLTranslator):
    meta = TranslatorMeta(
        name="MarkdownTranslator",
        format="markdown",
        description="Translate markdown formatted content",
    )

    def translate(self, markdown_text: str) -> str:
        """
        Translates json from source language to target language using a machine translation model.

        Args:
        - text: A string representing the input text to be translated.

        Returns:
        - Translated Json in string format
        """

        # Convert the markdown to html
        html = markdown.markdown(
            markdown_text,
            extensions=[
                "markdown.extensions.fenced_code",
                "markdown.extensions.md_in_html",
                "markdown.extensions.footnotes",
                "markdown.extensions.nl2br",
                "markdown.extensions.sane_lists",
                "markdown.extensions.wikilinks",
            ],
        )
        html_translation = super().translate(html)
        # Convert the html to markdown
        return markdownify(html_translation, heading_style="ATX")
