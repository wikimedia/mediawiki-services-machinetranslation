from .base import BaseTranslator
from .config import TranslatorConfig
from .indictrans import EnIndicTransTranslator, IndicEnTransTranslator
from .nllb import NLLBTranslator, NLLBWikipediaTranslator
from .opus import OpusTranslator
from .softcatala import SoftCatalaTranslator

from .factory import TranslatorFactory  # isort:skip

__all__ = [
    "BaseTranslator",
    "EnIndicTransTranslator",
    "IndicEnTransTranslator",
    "NLLBTranslator",
    "NLLBWikipediaTranslator",
    "OpusTranslator",
    "SoftCatalaTranslator",
    "TranslatorConfig",
    "TranslatorFactory",
]
