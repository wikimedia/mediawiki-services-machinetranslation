from unittest.mock import patch

from reverse import ReverseTransModel

from translator import HTMLTranslator

config = {}
with patch.object(
    HTMLTranslator, "getModel", return_value=ReverseTransModel(config)
) as mock_method:
    translator = HTMLTranslator(config, "en", "reverse")

testhtml = "<p id='mwCw'>\
The <b id='mwDA'>dodo</b> is an\
 <a rel='mw:WikiLink' href='./Extinction' title='Extinction' id='mwDw'>extinct</a>\
 <a rel='mw:WikiLink' href='./Flightless_bird' title='Flightless bird' id='mwEA'>flightless bird\
</a> that was <a rel='mw:WikiLink' href='./Endemism' title='Endemism' id='mwEQ'>endemic</a>\
 to the island of\
 <a rel='mw:WikiLink' href='./Mauritius' title='Mauritius' id='mwEg'>Mauritius</a>.</p>"

translated_html = "<p id='mwCw'>\
<a href='./Mauritius' id='mwEg' rel='mw:WikiLink' title='Mauritius'>\
Mauritius.</a> of island the to <a href='./Endemism' id='mwEQ' rel='mw:WikiLink' title='Endemism'>\
endemic.</a> was that <a href='./Flightless_bird' id='mwEA' rel='mw:WikiLink' title=\
'Flightless bird'>bird flightless</a> <a href='./Extinction' id='mwDw' rel='mw:WikiLink' \
title='Extinction'>extinct.</a> an is <b id='mwDA'>dodo.</b> The.</p>"


def test_translator():
    translation = translator.translate(testhtml)
    assert translation == translated_html.replace("'", '"', -1)
