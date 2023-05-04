import os
from ctranslate2 import Translator
from sentencepiece import SentencePieceProcessor
import logging
from typing import List
import logging.config

logging.config.fileConfig("logging.conf")


class BaseTranslator:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.inter_threads = int(os.getenv("CT2_INTER_THREADS", 1))
        self.intra_threads = int(os.getenv("CT2_INTRA_THREADS", 1))
        self.init()

    def getModel(self) -> Translator:
        return Translator(
            self.config.get("model"),  # Model
            # maximum number of batches executed in parallel.
            # => Increase this value to increase the throughput.
            inter_threads=self.inter_threads,
            #  number of OpenMP threads that is used per batch.
            # => Increase this value to decrease the latency on CPU.
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
        logging.info(
            f"inter_threads: { self.inter_threads}, intra_threads: {self.intra_threads} "
        )

    def translate(self, src_lang, tgt_lang, sentences) -> List[str]:
        raise Exception("Not implemented")
