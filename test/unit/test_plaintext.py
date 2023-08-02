from unittest.mock import patch

from reverse import ReverseTransModel

from translator import PlainTextTranslator

config = {}
with patch.object(
    PlainTextTranslator, "getModel", return_value=ReverseTransModel(config)
) as mock_method:
    translator = PlainTextTranslator(config, "en", "reverse")


tests = {
    "The quick brown fox jumps over the lazy dog": "dog lazy the over jumps fox brown quick The.",
    "War is peace. Freedom is slavery.": "peace is War. slavery is Freedom.",
}


def test_translator():
    for test in tests:
        result = tests[test]
        assert translator.translate(test) == result
