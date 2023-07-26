import logging
import logging.config
import multiprocessing
import os
from typing import List

from ctranslate2 import Translator
from sentencepiece import SentencePieceProcessor

from translator.normalizer import normalize

logging.config.fileConfig("logging.conf")

# As per https://opennmt.net/CTranslate2/performance.html
# By default CTranslate2 is compiled with intel MKL.
# It is observed that this setting has a significant positive performance impact.
os.environ["CT2_USE_EXPERIMENTAL_PACKED_GEMM"] = "1"


class BaseTranslator:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.inter_threads = int(os.getenv("CT2_INTER_THREADS", multiprocessing.cpu_count()))
        self.intra_threads = int(os.getenv("CT2_INTRA_THREADS", 0))
        self.init()

    def getModel(self) -> Translator:
        return Translator(
            self.config.get("model"),  # Model
            # maximum number of batches executed in parallel.
            # => Increase this value to increase the throughput.
            inter_threads=self.inter_threads,
            #  number of OpenMP threads that is used per batch.
            # => Increase this value to decrease the latency on CPU.
            # 0 to use a default value
            intra_threads=self.intra_threads,
            device="auto",
            compute_type="auto",
        )

    def getTokenizer(self) -> SentencePieceProcessor:
        sp = SentencePieceProcessor()
        sp.load(self.config.get("tokenizer"))
        return sp

    def init(self):
        self.model = self.getModel()
        self.tokenizer = self.getTokenizer()
        logging.info(f"{self.__class__.__name__} initialized.")
        logging.info(f"inter_threads: { self.inter_threads}, intra_threads: {self.intra_threads} ")

    def translate(self, src_lang: str, tgt_lang: str, text: str) -> str:
        """
        Translates text from source language to target language using a machine translation model.

        Args:
        - src_lang: A string representing the source language of the input text.
          Must be a valid language code.
        - tgt_lang: A string representing the target language for the translation output.
          Must be a valid language code.
        - text: A string representing the input text to be translated.

        Returns:
        - A string representing the translated text in the target language.
        """
        raise Exception("Not implemented")

    def preprocess(self, src_lang, text) -> str:
        return normalize(src_lang, text)

    def postprocess(self, tgt_lang, text) -> str:
        return normalize(tgt_lang, text)

    def compose_text(
        self,
        sentences: List[str],
        translated_sentences: List[str],
    ) -> str:
        """
        Composes translated text by joining its sentences.

        Args:
        - sentences: A list of strings which represent the original sentences of the text.
        - translated_sentences: A list of strings which represent the machine-translated
          sentences of the text.

        Returns:
        - A single string that represents the translated text by joining
          individual translated sentences.
        """
        translation: str = ""
        for index, sentence in enumerate(translated_sentences):
            if sentences[index] == "\n":
                translation += sentences[index]
            else:
                translation += sentence + " "
        return translation.strip()
