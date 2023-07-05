import logging
import logging.config

from translator import (
    EnIndicTransTranslator,
    IndicEnTransTranslator,
    NLLBTranslator,
    NLLBWikipediaTranslator,
    OpusTranslator,
)
from translator.base import BaseTranslator
from translator.config import TranslatorConfig
from translator.softcatala import SoftCatalaTranslator

logging.config.fileConfig("logging.conf")

translator_cache = {}


def TranslatorFactory(
    translator_config: TranslatorConfig, src_lang: str, tgt_lang: str
) -> BaseTranslator:
    translators = {
        "nllb200-600M": NLLBTranslator,
        "indictrans2-indic-en": IndicEnTransTranslator,
        "indictrans2-en-indic": EnIndicTransTranslator,
        "nllb-wikipedia": NLLBWikipediaTranslator,
        "opusmt-en-bcl": OpusTranslator,
        "opusmt-en-chr": OpusTranslator,
        "opusmt-en-to": OpusTranslator,
        "softcatala": SoftCatalaTranslator,
    }
    model = translator_config.language_pair_mapping[src_lang][tgt_lang]
    if model not in translator_cache:
        translator_cache[model] = translators.get(model)(translator_config.models.get(model))
    return translator_cache[model]
