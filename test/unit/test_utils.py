import pytest

from translator.models.utils import extract_potential_references

test_data = [
    ("empty string", "", []),
    ("single reference", "This is a sentence with [123].", ["[123]"]),
    ("multiple references", "Text with [a] and another one [b].", ["[a]", "[b]"]),
    ("numeric reference", "Text with [34].", ["[34]"]),
    ("invalid - too long", "This has an invalid reference [1234].", []),
    ("invalid - spaces", "This has an invalid reference [12 34].", []),
    ("invalid - non-alphanumeric", "This has an invalid reference [123$].", []),
    ("no brackets", "This has no reference 123.", []),
    ("multiple in brackets", "This has an invalid reference [123 456].", []),
]


@pytest.mark.parametrize("name, sentence, expected_output", test_data)
def test_extract_potential_references(name, sentence, expected_output):
    """
    Test extract_potential_references with different input sentences.
    """
    output = extract_potential_references(sentence)
    assert output == expected_output
