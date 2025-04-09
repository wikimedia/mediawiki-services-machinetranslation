import logging
import logging.config
import multiprocessing
import os
from math import ceil
from typing import List

from ctranslate2 import Translator
from sentencepiece import SentencePieceProcessor

from translator.models.config import MTModel
from translator.normalizer import normalize

logging.config.fileConfig("logging.conf")

# As per https://opennmt.net/CTranslate2/performance.html
# By default CTranslate2 is compiled with intel MKL.
# It is observed that this setting has a significant positive performance impact.
os.environ["CT2_USE_EXPERIMENTAL_PACKED_GEMM"] = "1"


class BaseModel:
    def __init__(self, config: MTModel):
        self.config = config
        self.model: Translator = None
        self.tokenizer = None
        self.inter_threads = int(os.getenv("CT2_INTER_THREADS", multiprocessing.cpu_count()))
        self.intra_threads = int(os.getenv("CT2_INTRA_THREADS", 0))
        self.init()

    def getModel(self) -> Translator:
        return Translator(
            self.config.model,  # Model
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
        sp.load(self.config.tokenizer)
        return sp

    def init(self):
        self.model = self.getModel()
        self.tokenizer = self.getTokenizer()
        logging.info(f"{self.__class__.__name__} initialized.")
        logging.info(f"inter_threads: {self.inter_threads}, intra_threads: {self.intra_threads} ")

    def translate(self, src_lang: str, tgt_lang: str, sentences: List[str]) -> List[str]:
        """
        Translates text from source language to target language using a machine translation model.

        Args:
        - src_lang: A string representing the source language of the input text.
          Must be a valid language code.
        - tgt_lang: A string representing the target language for the translation output.
          Must be a valid language code.
         - sentences: List of sentences to be translated.

        Returns:
        - List of translated sentences.
        """
        raise Exception("Not implemented")

    def preprocess(self, src_lang, text) -> str:
        return normalize(src_lang, text)

    def postprocess(self, tgt_lang, text) -> str:
        return normalize(tgt_lang, text)

    def batch_translate(
        self, src_lang: str, tgt_lang: str, sentences: List[str], batch_size=100
    ) -> List[str]:
        num_batches = ceil(len(sentences) / batch_size)  # Calculate the number of batches

        translated_sentences = []

        for i in range(num_batches):
            start = i * batch_size
            end = (i + 1) * batch_size

            batch = sentences[start:end]  # Get a batch of sentences

            batch_translations = self.translate(
                src_lang, tgt_lang, batch
            )  # Translate the batch of sentences

            # Append the translated sentences to the result list
            translated_sentences.extend(batch_translations)

        return translated_sentences


class ModelNotFoundException(Exception):
    "Raised when model is not found for given languages"

    pass
