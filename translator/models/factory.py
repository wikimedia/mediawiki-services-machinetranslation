import logging
import logging.config
from typing import Dict, List

from translator.models import (
    BaseModel,
    EnIndicTransModel,
    IndicEnTransModel,
    IndicTransModel,
    MADLAD400Model,
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
        "indictrans2-en-indic": EnIndicTransModel,
        "indictrans2-indic-en": IndicEnTransModel,
        "indictrans2-indic-indic": IndicTransModel,
        "madlad-400": MADLAD400Model,
        "nllb-wikipedia": NLLBWikipediaModel,
        "nllb200-600M": NLLBModel,
        "opusmt-en-bcl": OpusModel,
        "opusmt-en-bi": OpusModel,
        "opusmt-en-chr": OpusModel,
        "opusmt-en-guw": OpusModel,
        "opusmt-en-srn": OpusModel,
        "opusmt-en-to": OpusModel,
        "opusmt-en-ty": OpusModel,
        "opusmt-en-ve": OpusModel,
        "opusmt-sv-fi": OpusModel,
        "softcatala": SoftCatalaModel,
    }
    model_names: List[str] = translator_config.language_pair_mapping[src_lang][tgt_lang]
    if not model_name:
        # First one in the model names is the default model for the pair.
        model_name = model_names[0]
    if model_name not in translator_cache:
        model_config = translator_config.models.get(model_name)
        translator_cache[model_name] = translation_models.get(model_name)(model_config)
    return translator_cache[model_name]
