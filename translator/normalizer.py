import re
from typing import Dict

patterns_replacements: Dict[str, Dict[str, str]] = {}

# Adapted from scripts/tokenizer/normalize-punctuation.perl of Moses project
# https://github.com/moses-smt/mosesdecoder/
# Licensed under GPL v2+
patterns_replacements["en"] = {
    r"\r": "",  # Replaces carriage return with empty string
    r"\(": " (",  # Adds space before open parenthesis
    r"\)": ") ",  # Adds space after close parenthesis
    r"\s+": " ",  # Replaces multiple spaces with single space
    r"\) ([\.\!\:\?\;\,])": r")\1",  # Removes space between close parenthesis and punctuations
    r"\( ": "(",  # Removes space after open parenthesis
    r" \)": ")",  # Removes space before close parenthesis
    r"(\d) \%": r"\1%",  # Removes space between digits and percent symbol
    r" :": ":",  # Removes space before colon
    r" ;": ";",  # Removes space before semicolon
    r"“": '"',  # Replaces English opening quotation mark with English double quote
    r"”": '"',  # Replaces English closing quotation mark with English double quote
    r"–": "-",  # Replaces en dash with hyphen
    r"—": " - ",  # Replaces em dash with space, hyphen, and space
    r"´": "'",  # Replaces acute accent with apostrophe
    r"([a-z])‘([a-z])": r"\1'\2",  # Replaces left single quotation mark with apostrophe between lowercase letters
    r"([a-z])’([a-z])": r"\1'\2",  # Replaces right single quotation mark with apostrophe between lowercase letters
    r"‘": "'",  # Replaces left single quotation mark with apostrophe
    r"‚": "'",  # Replaces lower single quotation mark with apostrophe
    r"’": '"',  # Replaces right single quotation mark with English double quote
    r"\'\'": '"',  # Replaces two consecutive apostrophes with English double quote
    r"´´": '"',  # Replaces two consecutive acute accents with English double quote
    r"…": "...",  # Replaces ellipsis with three consecutive dots
    # Handle pseudo-spaces like nonbreaking space
    r" \%": "%",  # Removes nonbreak space before percent symbol
    r"nº ": "nº ",
    r" ºC": " ºC",  # Removes nonbreak space before "ºC"
    r" cm": " cm",  # Removes nonbreak space before "cm"
    r" \?": "?",  # Removes nonbreak space before question mark
    r" \!": "!",  # Removes nonbreak space before exclamation mark
    r" ;": ";",  # Removes nonbreak space before semicolon
    r", ": ", ",  # Removes nonbreak space after comma
}

patterns_replacements["fr"] = {
    r" « ": ' "',  # Replaces French opening quotation mark with space and English double quote
    r"« ": '"',  # Replaces French opening quotation mark with English double quote
    r"«": '"',  # Replaces French opening quotation mark with English double quote
    r" » ": '" ',  # Replaces French closing quotation mark with English double quote and space
    r" »": '"',  # Replaces French closing quotation mark with English double quote
    r"»": '"',  # Replaces French closing quotation mark with English double quote
}

patterns_replacements["de"] = {
    r"„": '"',  # Replaces German opening quotation mark with English double quote
}

patterns_replacements["ur"] = {
    r" ۔": "۔",  # Removes extra space before Arabic full stop
}

patterns_replacements["ks"] = patterns_replacements["ur"]


def normalize(language: str, text: str) -> str:
    if language in patterns_replacements:
        for pattern, replacement in patterns_replacements[language].items():
            text = re.sub(pattern, replacement, text)
    if language != "en":
        text = normalize("en", text)
    return text


if __name__ == "__main__":
    text = "Some text with „quotes“, “quotes”, –dashes—, and an accent on a letter´."
    print(normalize("en", text))
