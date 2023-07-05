from translator.normalizer import normalize


def test_normalize_en():
    assert normalize("en", "Hello!  How are you?") == "Hello! How are you?"
    assert normalize("en", "This is a test.") == "This is a test."
    assert normalize("en", "Mr. Smith went to Washington.") == "Mr. Smith went to Washington."
    assert normalize("en", "Can't we all just get along?") == "Can't we all just get along?"
    assert normalize("en", "That's all folks...") == "That's all folks..."


def test_normalize_fr():
    assert normalize("fr", "«Bonjour» dit-il.") == '"Bonjour" dit-il.'
    assert (
        normalize("fr", "«La vie est belle» disait ma grand-mère.")
        == '"La vie est belle" disait ma grand-mère.'
    )
    assert (
        normalize("fr", "J'ai visité la «Tour Eiffel» aujourd'hui.")
        == "J'ai visité la \"Tour Eiffel\" aujourd'hui."
    )
    assert (
        normalize("fr", "Pourquoi ne peut-on pas simplement dire «non»?")
        == 'Pourquoi ne peut-on pas simplement dire "non"?'
    )


def test_normalize_de():
    assert normalize("de", "„Guten Tag“, sagte er.") == '"Guten Tag", sagte er.'
    assert (
        normalize("de", "„Das ist ein Test“ beantwortete sie.")
        == '"Das ist ein Test" beantwortete sie.'
    )
    assert (
        normalize("de", "Ich mag „Berlin“ viel mehr als „München“.")
        == 'Ich mag "Berlin" viel mehr als "München".'
    )


def test_normalize_other():
    assert (
        normalize("es", "Hola. ¿Cómo estás?") == "Hola. ¿Cómo estás?"
    )  # Test non-supported language
    assert normalize("", "This is a test.") == "This is a test."  # Test empty language string
    assert normalize("en", "") == ""  # Test empty text string
