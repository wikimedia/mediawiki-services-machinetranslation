from unittest.mock import patch

from reverse import ReverseTransModel

from translator import MarkdownTranslator

config = {}
with patch.object(
    MarkdownTranslator, 'getModel', return_value=ReverseTransModel(config)
) as mock_method:
    translator = MarkdownTranslator(config, 'en', 'reverse')

testmd = """# Introduction

The **dodo** is an [extinct](./Extinction 'Extinction') [flightless bird]\
(./Flightless_bird 'Flightless bird') that was [endemic](./Endemism 'Endemism')\
 to the island of [Mauritius](./Mauritius 'Mauritius').
"""

translated_md = """# Introduction.


[Mauritius.](./Mauritius "Mauritius") of island the to [endemic.](./Endemism "Endemism")\
 was that [bird flightless](./Flightless_bird "Flightless bird")\
 [extinct.](./Extinction "Extinction") an is **dodo.** The.

"""

def test_translator():
    translation = translator.translate(testmd)
    assert translation == translated_md
