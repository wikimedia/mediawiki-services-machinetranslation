import logging
import logging.config
from typing import Dict

from translator.models import (
    BaseModel,
    EnIndicTransModel,
    IndicEnTransModel,
    ModelConfig,
    NLLBModel,
    NLLBWikipediaModel,
    OpusModel,
    SoftCatalaModel,
)

logging.config.fileConfig("logging.conf")

translator_cache: Dict[str, BaseModel] = {}


def ModelFactory(translator_config: ModelConfig, src_lang: str, tgt_lang: str) -> BaseModel:
    translation_models = {
        "nllb200-600M": NLLBModel,
        "indictrans2-indic-en": IndicEnTransModel,
        "indictrans2-en-indic": EnIndicTransModel,
        "nllb-wikipedia": NLLBWikipediaModel,
        "opusmt-en-bcl": OpusModel,
        "opusmt-en-bi": OpusModel,
        "opusmt-en-chr": OpusModel,
        "opusmt-en-guw": OpusModel,
        "opusmt-en-srn": OpusModel,
        "opusmt-en-to": OpusModel,
        "opusmt-en-ty": OpusModel,
        "opusmt-en-ve": OpusModel,
        "softcatala": SoftCatalaModel,
    }
    model = translator_config.language_pair_mapping[src_lang][tgt_lang]
    if model not in translator_cache:
        model_config = translator_config.models.get(model)
        translator_cache[model] = translation_models.get(model)(model_config)
    return translator_cache[model]
