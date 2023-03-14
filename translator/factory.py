import logging

import logging.config
from translator.base import BaseTranslator
from translator.config import TranslatorConfig
from translator.nllb import NLLBTranslator, NLLBWikipediaTranslator

logging.config.fileConfig("logging.conf")

translator_cache={}

def TranslatorFactory(translator_config: TranslatorConfig, src_lang: str, tgt_lang: str) -> BaseTranslator:
    translators = {
        "nllb200-600M": NLLBTranslator,
        "nllb-wikipedia": NLLBWikipediaTranslator
    }
    model = translator_config.language_pair_mapping[src_lang][tgt_lang]
    if model not in translator_cache:
        translator_cache[model] = translators.get(model)(translator_config.models.get(model));
    return translator_cache[model]

sentences = """
Jazz is a music genre that originated in the African-American communities of New Orleans, Louisiana, United States, in the late 19th and early 20th centuries, with its roots in blues and ragtime.
Since the 1920s Jazz Age, it has been recognized as a major form of musical expression in traditional and popular music, linked by the common bonds of African-American and European-American musical parentage.
Jazz is characterized by swing and blue notes, complex chords, call and response vocals, polyrhythms and improvisation.
Jazz has roots in West African cultural and musical expression, and in African-American music traditions.
""".strip().splitlines()

if __name__ == "__main__":
    config = TranslatorConfig()
    print(
        TranslatorFactory(config, "en", "ig").translate(
           "en", "ig", sentences
        )
    )
