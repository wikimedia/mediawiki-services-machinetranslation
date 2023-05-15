import multiprocessing
from ctranslate2 import Translator
from sentencepiece import SentencePieceProcessor
import logging
import json
from pathlib import Path
from typing import List
import logging.config

logging.config.fileConfig("logging.conf")
models = json.loads(Path("models.json").read_text())
config = json.loads(Path("config.json").read_text())

translator_cache = []


class BaseTranslator:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.init()

    def getModel(self) -> Translator:
        return Translator(
            self.config.get("model"),  # Model
            # maximum number of batches executed in parallel.
            # => Increase this value to increase the throughput.
            inter_threads=multiprocessing.cpu_count(),
            #  number of OpenMP threads that is used per batch.
            # => Increase this value to decrease the latency on CPU.
            intra_threads=multiprocessing.cpu_count(),
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
        logging.info(f"{self.__class__.__name__} initialized")

    def translate(self, src_lang, tgt_lang, sentences) -> List[str]:
        raise Exception("Not implemented")


class NLLBTranslator(BaseTranslator):
    MODEL = "nllb200-600M"

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        return self.tokenizer.encode(content, out_type=str) + ["</s>", src_lang]

    def detokenize(self, content: str) -> str:
        return self.tokenizer.decode(content)

    def get_target_prefixes(self, tgt_lang: str):
        return [tgt_lang]

    def translate(
        self, src_lang: str, tgt_lang: str, sentences: List[str]
    ) -> List[str]:
        """
        Translate the text from source lang to target lang
        """
        sentences_tokenized = []
        translation = []
        target_prefixes = []
        assert self.model
        for sentence in sentences:
            sentences_tokenized.append(self.tokenize(src_lang, tgt_lang, sentence))
            target_prefix = self.get_target_prefixes(tgt_lang)
            if target_prefix:
                target_prefixes.append(target_prefix)

        print(target_prefixes)
        results = self.model.translate_iterable(
            sentences_tokenized,
            target_prefix=target_prefixes if len(target_prefixes) else None,
            asynchronous=True,
            batch_type="tokens",
            max_batch_size=1024,
            beam_size=1,
        )
        for result in results:
            translation.append(self.detokenize(result.hypotheses[0][1:]))
        return translation


class NLLBWikipediaTranslator(NLLBTranslator):
    MODEL = "nllb-wikipedia"

    def get_target_prefixes(self, tgt_lang: str):
        return None

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        src = "__" + src_lang.split("_")[0] + "__"
        target = "__" + tgt_lang.split("_")[0] + "__"
        return [target] + self.tokenizer.encode(content, out_type=str) + ["</s>", src]


def TranslatorFactory(src_lang, tgt_lang):
    """Factory Method"""
    translator = NLLBTranslator
    return translator(models[NLLBTranslator.MODEL])


sentences = """
Jazz is a music genre that originated in the African-American communities of New Orleans, Louisiana, United States, in the late 19th and early 20th centuries, with its roots in blues and ragtime.
Since the 1920s Jazz Age, it has been recognized as a major form of musical expression in traditional and popular music, linked by the common bonds of African-American and European-American musical parentage.
Jazz is characterized by swing and blue notes, complex chords, call and response vocals, polyrhythms and improvisation.
Jazz has roots in West African cultural and musical expression, and in African-American music traditions.
""".strip().splitlines()

if __name__ == "__main__":
    print(
        TranslatorFactory("eng_Latn", "ibo_Latn").translate(
            "eng_Latn", "ibo_Latn", sentences
        )
    )

    print(
        NLLBWikipediaTranslator(models[NLLBWikipediaTranslator.MODEL]).translate(
            "eng_Latn", "ibo_Latn", sentences
        )
    )
