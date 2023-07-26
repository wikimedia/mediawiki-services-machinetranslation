import logging
import logging.config
from typing import List

from translator.models import BaseModel

logging.config.fileConfig("logging.conf")


class SoftCatalaModel(BaseModel):
    MODEL = "softcatala"

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        return self.tokenizer.encode(content, out_type=str)

    def detokenize(self, content: str) -> str:
        return self.tokenizer.decode(content).replace("▁", " ").strip()

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

        translated_sentences: List[str] = []
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
            translated_sentences.append(translated_sentence)

        return translated_sentences
