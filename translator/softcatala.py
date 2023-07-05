import logging
import logging.config
from typing import List

from translator import BaseTranslator

logging.config.fileConfig("logging.conf")


class SoftCatalaTranslator(BaseTranslator):
    MODEL = "softcatala"

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        return self.tokenizer.encode(content, out_type=str)

    def detokenize(self, content: str) -> str:
        return self.tokenizer.decode(content).replace("▁", " ").strip()

    def translate(self, src_lang: str, tgt_lang: str, sentences: List[str]) -> List[str]:
        """
        Translate the text from source lang to target lang
        """
        translation: List[str] = []
        sentences_tokenized: List[str] = []

        for sentence in sentences:
            sentence = self.preprocess(src_lang, sentence)
            sentences_tokenized.append(self.tokenize(src_lang, tgt_lang, sentence))

        results = self.model.translate_iterable(
            sentences_tokenized,
            asynchronous=True,
            batch_type="tokens",
            max_batch_size=1024,
            beam_size=1,
        )

        for result in results:
            translated_sentence = self.detokenize(result.hypotheses[0])
            translated_sentence = self.postprocess(tgt_lang, translated_sentence)
            translation.append(translated_sentence)
        return translation
