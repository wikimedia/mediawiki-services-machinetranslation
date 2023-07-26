import re

from translator.segmenter.abbreviations import BaseAbbreviation


class English(BaseAbbreviation):
    language = "en"

    @staticmethod
    def is_abbreviation(head: str, tail: str):
        """
        Do not break in abbreviations. Example D. John, St. Peter
        In the case of "This is Dr. Watson", head is "This is Dr", tail is " Watson"
        """
        lastWord = re.findall(r"\w*$", head)[0]
        # Exclude at most 2 letter abbreviations. Examples: T. Dr. St. Jr. Sr. Ms. Mr.
        # But not all caps like "UK." as in  "UK. Not US",
        if (
            len(lastWord) <= 2
            and re.match(r"^\W*[A-Z][a-z]?$", lastWord)
            and re.match(r"^\W*[A-Z]", tail)
        ):
            return True

        return False
