from unittest.mock import patch

from reverse import ReverseTransModel

from translator import SVGTranslator

config = {}
with patch.object(SVGTranslator, "getModel", return_value=ReverseTransModel(config)) as mock_method:
    translator = SVGTranslator(config, "en", "reverse")

test_svg = """
<svg viewBox="0 0 240 80" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <text x="20" y="35" class="small">My cat is grumpy!</text>
  <path id="my_path" d="M 20,20 C 40,40 80,40 100,20" />
  <text>
    <textPath xlink:href="#my_path">This text follows a curve.</textPath>
  </text>
</svg>
"""


translated_svg = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"\
 viewBox="0 0 240 80">
  <text x="20" y="35" class="small">grumpy! is cat My</text>
  <path id="my_path" d="M 20,20 C 40,40 80,40 100,20" />
  <text>
    <textPath xlink:href="#my_path">curve a follows text This.</textPath>
  </text>
</svg>
"""


def test_translator():
    translation = translator.translate(test_svg)
    print(translation)
    assert translation.strip() == translated_svg.strip()
