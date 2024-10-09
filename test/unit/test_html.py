import re
from unittest.mock import patch

from reverse import ReverseTransModel

from translator import HTMLTranslator
from translator.html import fuzzy_find

config = {}
with patch.object(
    HTMLTranslator, "getModel", return_value=ReverseTransModel(config)
) as mock_method:
    translator = HTMLTranslator(config, "en", "reverse")

test_dodo_html = "<p id='mwCw'>\
The <b id='mwDA'>dodo</b> is an\
 <a rel='mw:WikiLink' href='./Extinction' title='Extinction' id='mwDw'>extinct</a>\
 <a rel='mw:WikiLink' href='./Flightless_bird' title='Flightless bird' id='mwEA'>flightless bird\
</a> that was <a rel='mw:WikiLink' href='./Endemism' title='Endemism' id='mwEQ'>endemic</a>\
 to the island of\
 <a rel='mw:WikiLink' href='./Mauritius' title='Mauritius' id='mwEg'>Mauritius</a>.</p>"

translated_dodo_html = """<p id="mwCw">\
<a href="./Mauritius" id="mwEg" rel="mw:WikiLink" title="Mauritius">Mauritius</a> \
of island the to <a href="./Endemism" id="mwEQ" rel="mw:WikiLink" title="Endemism">\
endemic</a> was that <a href="./Flightless_bird" id="mwEA" rel="mw:WikiLink" \
title="Flightless bird">bird flightless</a> <a href="./Extinction" id="mwDw" rel="mw:WikiLink" \
title="Extinction">extinct</a> an is <b id="mwDA">dodo</b> The.</p>"""

test_span_with_sup_html = """\
<section id="cxTargetSection2" data-mw-section-number="0">
<p id="mwHQ">
<span data-segmentid="307" class="cx-segment">The JWST was launched 25 December 2021 on an ESA.
<sup typeof="mw:Extension/ref" data-mw="{}" class="mw-ref reference" data-cx="{}" about="#mwt120" \
id="cite_ref-about_11-0" rel="dc:references">
<a href="./James_Webb_Space_Telescope#cite_note-about-11" id="mwMQ" \
style="counter-reset: mw-Ref 4;">
<span class="mw-reflink-text" id="mwMg">[4]</span>
</a></sup>
</span>
</p>
</section>
"""


translated_span_with_sup_html = """\
<section data-mw-section-number="0" id="cxTargetSection2">\
<p id="mwHQ"><span class="cx-segment" data-segmentid="307">\
ESA an on 2021 December 25 launched was JWST The.
<sup about="#mwt120" class="mw-ref reference" \
data-cx="{}" data-mw="{}" id="cite_ref-about_11-0" rel="dc:references" typeof="mw:Extension/ref">
<a href="./James_Webb_Space_Telescope#cite_note-about-11" id="mwMQ" \
style="counter-reset: mw-Ref 4;">
<span class="mw-reflink-text" id="mwMg">[4]</span>
</a></sup> </span></p></section>"""


test_span_with_sup_html_dense_format = """\
<section id="cxTargetSection2" data-mw-section-number="0"><p id="mwHQ">\
<span data-segmentid="307" class="cx-segment">The JWST was launched 25 December 2021 on an ESA.\
<sup typeof="mw:Extension/ref" data-mw="{}" class="mw-ref reference" data-cx="{}" about="#mwt120" \
id="cite_ref-about_11-0" rel="dc:references"><a \
href="./James_Webb_Space_Telescope#cite_note-about-11" id="mwMQ" \
style="counter-reset: mw-Ref 4;"><span class="mw-reflink-text" id="mwMg">[4]</span> \
</a></sup></span></p></section>"""

translated_span_with_sup_html_dense_format = """\
<section data-mw-section-number="0" id="cxTargetSection2">\
<p id="mwHQ"><span class="cx-segment" data-segmentid="307">ESA.<sup about="#mwt120" \
class="mw-ref reference" data-cx="{}" data-mw="{}" id="cite_ref-about_11-0" \
rel="dc:references" typeof="mw:Extension/ref"><a href="./James_Webb_Space_Telescope#\
cite_note-about-11" id="mwMQ" style="counter-reset: mw-Ref 4;"><span class="mw-reflink-text" \
id="mwMg">[4]</span> </a></sup> an on 2021 December 25 launched was JWST The. </span>\
</p></section>"""

test_list = """<div>\
<p>Following are some examples of fruits:</p>
<ul><li>Banana</li><li>Apple</li><li>Orange</li><li>Kiwi</li><li>Papaya</li></ul>
</div>"""

translated_list = """<div>\
<p>fruits: of examples some are Following</p>\
<ul><li>Banana</li><li>Apple</li><li>Orange</li><li>Kiwi</li><li>Papaya</li>\
</ul></div>"""

test_references_ml = """\
<p>1891 ജൂലൈ 30 -ന് തന്റെ 35 ആം വയസ്സിൽ ടെസ്‌ല <a href="/wiki/United_States_of_America" \
class="mw-redirect" title="United States of America">അമേരിക്കൻ ഐക്യനാടുകളിലെ</a> \
<a href="/w/index.php?title=Naturalization&amp;action=edit&amp;redlink=1" class="new" \
title="Naturalization (ഇതുവരെ എഴുതപ്പെട്ടിട്ടില്ല)">പൗരത്വം</a> നേടി.<sup id="cite_ref-NYcourts_95-0" \
class="reference"><a href="#cite_note-NYcourts-95">[95]</a></sup><sup \
id="cite_ref-FOOTNOTECarlson2013138_96-0" class="reference">\
<a href="#cite_note-FOOTNOTECarlson2013138-96">[96]</a>\
</sup> അതേ വർഷം അദ്ദേഹം <a href="/w/index.php?title=Tesla_coil&amp;action=edit&amp;redlink=1" \
class="new" title="Tesla coil (ഇതുവരെ എഴുതപ്പെട്ടിട്ടില്ല)">ടെസ്‌ല കോയിലിനു</a> പേറ്റന്റും നേടി.\
<sup id="cite_ref-Uth_97-0" class="reference"><a href="#cite_note-Uth-97" title="">[97]</a></sup>
</p>
"""

# All the three references should appear in translation
translated_references_ml = """\
<p>നേടി.<sup class="reference" id="cite_ref-NYcourts_95-0"><a href="#cite_note-NYcourts-95">[95]\
</a></sup><sup class="reference" id="cite_ref-FOOTNOTECarlson2013138_96-0">\
<a href="#cite_note-FOOTNOTECarlson2013138-96">[96]</a></sup> \
<a class="new" href="/w/index.php?title=Naturalization&amp;action=edit&amp;redlink=1" \
title="Naturalization (ഇതുവരെ എഴുതപ്പെട്ടിട്ടില്ല)">പൗരത്വം</a> <a class="mw-redirect" \
href="/wiki/United_States_of_America" title="United States of America">ഐക്യനാടുകളിലെ അമേരിക്കൻ</a> \
ടെസ്‌ല വയസ്സിൽ ആം 35 തന്റെ -ന് 30 ജൂലൈ 1891. നേടി.<sup class="reference" id="cite_ref-Uth_97-0">\
<a href="#cite_note-Uth-97" title="">[97]</a></sup> പേറ്റന്റും \
<a class="new" href="/w/index.php?title=Tesla_coil&amp;action=edit&amp;redlink=1" \
title="Tesla coil (ഇതുവരെ എഴുതപ്പെട്ടിട്ടില്ല)">കോയിലിനു ടെസ്‌ല</a> അദ്ദേഹം വർഷം അതേ. \
</p>\
"""

test_repeated_element = """\
<p><a href="./GNU">GNU</a> is an abbreviation of \
<a href="./GNU">GNU</a> is not <a href="./Unix">Unix</a></p>
"""

translated_repeated_element = """\
<p><a href="./Unix">Unix</a> not is <a href="./GNU">GNU</a> of \
abbreviation an is <a href="./GNU">GNU</a></p>
"""

test_repeated_element_across_sentences = """\
<section id="cxTargetSection0" data-mw-cx-source="undefined" data-mw-section-number="0">
<p id="mwAg">
<span data-segmentid="4" class="cx-segment"><a href="./Unix">Unix</a> not is \
<a href="./GNU">GNU</a> of abbreviation an is <a href="./GNU">GNU</a></span>
<span data-segmentid="4" class="cx-segment"><a href="./Unix">Unix</a> not is \
<a href="./GNU">GNU</a> of abbreviation an is <a href="./GNU">GNU</a></span>
</p>
</section>
"""

translated_repeated_element_across_sentences = """\
<section data-mw-cx-source="undefined" data-mw-section-number="0" id="cxTargetSection0">\
<p id="mwAg">\
<span class="cx-segment" data-segmentid="4"><a href="./GNU">GNU</a> is an abbreviation of \
<a href="./GNU">GNU</a> is not <a href="./Unix">Unix</a></span>\
<span class="cx-segment" data-segmentid="4"><a href="./GNU">GNU</a> is an abbreviation of \
<a href="./GNU">GNU</a> is not <a href="./Unix">Unix</a></span>\
</p>\
</section>
"""

tests = [
    {"source": test_dodo_html, "translation": translated_dodo_html},
    {"source": test_dodo_html, "translation": translated_dodo_html},
    {"source": test_list, "translation": translated_list},
    {"source": test_span_with_sup_html, "translation": translated_span_with_sup_html},
    {
        "source": test_span_with_sup_html_dense_format,
        "translation": translated_span_with_sup_html_dense_format,
    },
    {
        "source": test_references_ml,
        "translation": translated_references_ml,
    },
    {
        "source": test_repeated_element,
        "translation": translated_repeated_element,
    },
    {
        "source": test_repeated_element_across_sentences,
        "translation": translated_repeated_element_across_sentences,
    },
]


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def test_translator():
    for test in tests:
        translation = translator.translate(test["source"])
        print("--")
        print(translation)
        print("--")
        print(test["translation"])
        print("--")
        assert normalize(translation) == normalize(test["translation"])


def test_fuzzy_find():
    # Test exact match
    text = "The quick brown fox jumps over the lazy dog."
    key = "quick brown fox"
    expected = ("quick brown fox", 4, 19)
    assert fuzzy_find(text, key) == expected

    # Test fuzzy match with minor differences
    text = "The quick brown fox jumps over the lazy dog."
    key = "quick brown fix"
    expected = ("quick brown fox", 4, 19)
    assert fuzzy_find(text, key) == expected

    # Test fuzzy match with major differences
    text = "The quick brown fox jumps over the lazy dog."
    key = "quick brown fixes"
    expected = (None, -1, -1)
    assert fuzzy_find(text, key) == expected

    # Test fuzzy match with punctuation
    text = "The quick brown fox jumps over the lazy dog."
    key = "."
    expected = (None, -1, -1)
    assert fuzzy_find(text, key) == expected

    # Test no match
    text = "The quick brown fox jumps over the lazy dog."
    key = "slow green turtle"
    expected = (None, -1, -1)
    assert fuzzy_find(text, key) == expected

    # Test match with numbers
    text = "The year is 2023 and the month is October."
    key = "2023"
    expected = ("2023", 12, 16)
    assert fuzzy_find(text, key) == expected

    # Test match with numbers, approximation not applied for numbers
    text = "The year is 2023 and the month is October."
    key = "2024"
    expected = (None, -1, -1)
    assert fuzzy_find(text, key) == expected

    # Test match with reference
    text = "The year is 2023 and the month is October[12]."
    key = "[12]"
    expected = ("[12]", 41, 45)
    assert fuzzy_find(text, key) == expected

    # Test match with reference - no approximation
    text = "The year is 2023 and the month is October[12345]."
    key = "[12435]"
    expected = (None, -1, -1)
    assert fuzzy_find(text, key) == expected

    # Test match with special characters
    text = "Hello, world! Welcome to the universe."
    key = "World!"
    expected = ("world!", 7, 13)
    assert fuzzy_find(text, key) == expected

    # Test match with leading and trailing spaces
    text = "   The quick brown fox jumps over the lazy dog.   "
    key = "quick brown fox"
    expected = ("quick brown fox", 7, 22)
    assert fuzzy_find(text, key) == expected

    # Test match with multiple occurrences
    text = "The quick brown fox and the quick brown fox."
    key = "quick brown fox"
    expected = ("quick brown fox", 4, 19)
    assert fuzzy_find(text, key) == expected

    # Test match with search_start parameter
    text = "The quick brown fox and the quick brown fox."
    key = "quick brown fox"
    expected = ("quick brown fox", 28, 43)
    assert fuzzy_find(text, key, search_start=20) == expected

    # Test match with search_start parameter and prefix
    text = "The quick brown fox and the quick brown fox."
    key = "quick brow"
    expected = ("quick brown", 28, 39)
    assert fuzzy_find(text, key, search_start=20) == expected

    # Test match with search_start parameter and prefix
    text = "The quick brown fox and the quick brownification! fox."
    key = "quick bro"
    expected = ("quick brownification", 28, 48)
    assert fuzzy_find(text, key, search_start=20) == expected

    # Test match with search_start parameter and no match
    text = "The quick brown fox"
    key = "something else"
    expected = (None, -1, -1)
    assert fuzzy_find(text, key, search_start=20) == expected
