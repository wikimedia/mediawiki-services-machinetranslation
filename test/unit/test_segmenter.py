from translator.segmenter import segment

tests = {
    "en": {
        "Roses Are Red. Violets Are Blue": ["Roses Are Red. ", "Violets Are Blue"],
        "Hello! How are you?": ["Hello! ", "How are you?"],
        "This is a test.": ["This is a test."],
        "Mr. Smith went to Washington.": ["Mr. Smith went to Washington."],
        "What a suprise?!": ["What a suprise?!"],
        "That's all folks...": ["That's all folks..."],
        "First line\nSecond line": ["First line", "\n", "Second line"],
        "First line\nSecond line\n\nThird line": [
            "First line",
            "\n",
            "Second line",
            "\n",
            "\n",
            "Third line",
        ],
        "This is UK. Not US": ["This is UK. ", "Not US"],
        "This balloon costs $1.20": ["This balloon costs $1.20"],
    },
    "ml": {
        "ഇത് ഡോ. ശിവൻ. ഇദ്ദേഹമാണ് ഞാൻ പറഞ്ഞയാൾ": ["ഇത് ഡോ. ശിവൻ. ", "ഇദ്ദേഹമാണ് ഞാൻ പറഞ്ഞയാൾ"],
        "ഇത് മി. കെ. പി. മോഹനൻ": ["ഇത് മി. കെ. പി. മോഹനൻ"],
        "ഇത് പ്രൊ. കെ.പി. മോഹനൻ": ["ഇത് പ്രൊ. കെ.പി. മോഹനൻ"],
        "ഇത് Dr. മോഹനൻ": ["ഇത് Dr. മോഹനൻ"],
    },
}


def test_segment():
    for lang in tests:
        for test in tests[lang]:
            assert segment(lang, test) == tests[lang][test]
