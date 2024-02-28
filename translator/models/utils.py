import re
from typing import Dict, List


def extract_potential_references(sentence: str) -> List[str]:
    r"""
    The regular expression r"(\[\s*[0-9a-z]{,3}\s*\])" matches any substring that:

    Starts with a square bracket [
    Is followed by zero or more whitespace characters \s*
    Is followed by up to three alphanumeric characters [0-9a-z]{,3}
    Is followed by zero or more whitespace characters \s*
    Ends with a square bracket ]
    Example strings that the regex accepts:

    [1]
    [123]
    [abc]
    [ 1 ]
    [ abc ]
    Example strings that the regex does not accept:

    [1234] (too many alphanumeric characters)
    [1 2] (multiple alphanumeric characters separated by a space)
    [123abc] (alphanumeric characters and non-alphanumeric characters)
    123 (no square brackets)
    [123 456] (multiple references in a single string)
    """
    return re.findall(r"(\[\s*[0-9a-z]{,3}\s*\])", sentence)


def apply_missing_references(
    reference_map: Dict[str, List[str]], translated_sentences: List[str]
) -> List[str]:
    """Applies missing references to translated sentences.

    Args:
        reference_map (Dict[str, List[str]]): A dictionary mapping sentences to lists of references.
        translated_sentences (List[str]): A list of translated sentences.

    Returns:
        List[str]: A list of translated sentences with missing references added.
    """

    translated_sentences_with_ref = []
    i = 0
    for sentence in reference_map:
        translated_sentence = translated_sentences[i]
        original_refs = reference_map.get(sentence)
        existing_refs: List[str] = extract_potential_references(translated_sentence)
        for existing_ref in existing_refs:
            if existing_ref not in original_refs:
                translated_sentence = translated_sentence.replace(existing_ref, "")

        for ref in original_refs:
            if ref not in translated_sentence:
                translated_sentence += ref

        translated_sentences_with_ref.append(translated_sentence)
        i = i + 1

    return translated_sentences_with_ref
