import re
from typing import List

from . import languages
from .abbreviations import AbbreviationsRegistry
from .terminators import GLOBAL_SENTENCE_TERMINATORS


def is_abbreviation(language: str, head: str, tail: str) -> str:
    if language in AbbreviationsRegistry.REGISTRY:
        langInst = AbbreviationsRegistry.REGISTRY[language]()
    else:
        # Fallback to English
        langInst = AbbreviationsRegistry.REGISTRY["en"]()

    return langInst.is_abbreviation(head, tail)


def findBoundary(language, text, match):
    tail = text[match.start() + 1 :]
    head = text[: match.start()]

    # Trailing non-final punctuation: not a sentence boundary
    if re.match(r"^[,;:]", tail):
        return None
    # Next word character is number or lower-case: not a sentence boundary
    if re.match(r"^\W*[0-9a-z]", tail):
        return None
    if is_abbreviation(language, head, tail):
        return None
    # Include any closing punctuation and trailing space
    return match.start() + 1 + len(re.match(r"^['”\"’]*\s*", tail).group(0))


def segment(language, text: str) -> List[str]:
    sentences = []
    paragraphs = text.splitlines()
    paragraph_index = 0
    for paragraph in paragraphs:
        if paragraph_index > 0:
            sentences.append("\n")
        boundaries = [0]
        matches = re.finditer(r"[%s]" % "".join(GLOBAL_SENTENCE_TERMINATORS), paragraph)
        prev_boundary = 0
        for match in matches:
            boundary = findBoundary(language, paragraph, match)
            if prev_boundary + 1 == boundary:
                boundaries[-1] = boundary
                prev_boundary = boundary
                continue
            if boundary is not None:
                boundaries.append(boundary)
                prev_boundary = boundary

        for i, j in zip(boundaries, boundaries[1:] + [None]):
            sentence = paragraph[i:j]
            if len(sentence):
                sentences.append(sentence)
        paragraph_index += 1

    return sentences


__all__ = ["segment", "languages"]
