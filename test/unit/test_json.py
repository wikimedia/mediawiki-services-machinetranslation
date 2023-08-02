import json
from unittest.mock import patch

from reverse import ReverseTransModel

from translator import JSONTranslator

config = {}
with patch.object(
    JSONTranslator, "getModel", return_value=ReverseTransModel(config)
) as mock_method:
    translator = JSONTranslator(config, "en", "reverse")

biryani = {
    "id": 1,
    "title": "Chicken Biryani",
    "description": "Chicken Biryani is a savory chicken and rice dish",
    "ingredients": ["Vegetable oil", "Garlic", "Ginger", "Rice"],
}

biryani_reverse = {
    "id": 1,
    "title": "Biryani Chicken.",
    "description": "dish rice and chicken savory a is Biryani Chicken.",
    "ingredients": ["oil Vegetable.", "Garlic.", "Ginger.", "Rice."],
}


def test_translator():
    translation = translator.translate(json.dumps(biryani))
    expected = json.dumps(biryani_reverse, indent=2, ensure_ascii=False)

    assert translation == expected
