import logging
import logging.config
from typing import List

from translator import BaseTranslator
from translator.segmenter import segment

logging.config.fileConfig("logging.conf")


class OpusTranslator(BaseTranslator):
    MODEL = "opusmt"

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        return self.tokenizer.encode(content, out_type=str)

    def detokenize(self, content: str) -> str:
        return self.tokenizer.decode(content).replace("▁", " ").strip()

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
        sentences: List[str] = segment(src_lang, text)
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
            repetition_penalty=2,
        )

        for result in results:
            translated_sentence = self.detokenize(result.hypotheses[0][1:])
            translated_sentence = self.postprocess(tgt_lang, translated_sentence)
            translated_sentences.append(translated_sentence)
        return self.compose_text(sentences, translated_sentences)
