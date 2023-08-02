import re

from translator.segmenter.abbreviations import BaseAbbreviation

abbreviations = [
    "ഡോ",  # Dr
    "Dr",  # Writing Dr as such inside Malayalam is common
    "പ്രൊ",  # Prof
    "Prof",  # Prof
    "മി",  # Mr, or Minister
    "Mr",
    "Ms",
    "Mrs",
    "ശ്രീ",  # Formal addressing - male
    "ശ്രീമതി",  # Formal addressing - female
    "ബഹു",  # Respected
    # Transliteration of English alphabets
    "എ",
    "ബി",
    "സി",
    "ഡി",
    "എഫ്",
    "ജി",
    "എച്",
    "എച്ച്",
    "ഐ",
    "ജെ",
    "കെ",
    "എൽ",
    "എം",
    "എൻ",
    "ഒ",
    "ഓ",
    "പി",
    "ക്യു",
    "ക്യൂ",
    "ആർ",
    "ടി",
    "യു",
    "യൂ",
    "വി",
    "ഡബ്ല്യു",
    "ഡബ്ള്യു",
    "എക്സ്",
    "വൈ",
    "ഇസഡ്",
]


class Malayalam(BaseAbbreviation):
    language = "ml"

    @staticmethod
    def is_abbreviation(head: str, tail: str):
        """
        Do not break in abbreviations. Example കെ. പി. മോഹനൻ, ഡോ. സന്തോഷ്
        In the case of "ഇത് ഡോ. ശിവൻ", head is "ഇത് ഡോ", tail is " ശിവൻ"
        """
        lastWord = re.split(r"[\s\.]+", head)[-1]
        return lastWord in abbreviations
