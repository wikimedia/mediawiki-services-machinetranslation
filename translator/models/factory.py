import logging
import logging.config
from typing import Dict, List

from translator.models import (
    BaseModel,
    EnIndicTransModel,
    IndicEnTransModel,
    IndicTransModel,
    ModelConfiguration,
    NLLBModel,
    NLLBWikipediaModel,
    OpusModel,
    SoftCatalaModel,
)

logging.config.fileConfig("logging.conf")

translator_cache: Dict[str, BaseModel] = {}


def ModelFactory(
    translator_config: ModelConfiguration, src_lang: str, tgt_lang: str, model_name: str = None
) -> BaseModel:
    translation_models = {
        "nllb200-600M": NLLBModel,
        "indictrans2-indic-indic": IndicTransModel,
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
    model_names: List[str] = translator_config.language_pair_mapping[src_lang][tgt_lang]
    if not model_name:
        model_name = model_names[-1]
    if model_name not in translator_cache:
        model_config = translator_config.models.get(model_name)
        translator_cache[model_name] = translation_models.get(model_name)(model_config)
    return translator_cache[model_name]
