import logging
import logging.config
from typing import List

from translator import BaseTranslator, languages
from translator.segmenter import segment

logging.config.fileConfig("logging.conf")


class NLLBTranslator(BaseTranslator):
    MODEL = "nllb200-600M"

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        return self.tokenizer.encode(content, out_type=str) + [
            "</s>",
            languages.get_wikicode_from_nllb(src_lang),
        ]

    def detokenize(self, content: str) -> str:
        return self.tokenizer.decode(content)

    def get_target_prefixes(self, tgt_lang: str):
        return [languages.get_wikicode_from_nllb(tgt_lang)]

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
        sentences_tokenized = []
        translated_sentences: List[str] = []
        target_prefixes = []
        assert self.model
        for sentence in sentences:
            sentence = self.preprocess(src_lang, sentence)
            sentences_tokenized.append(self.tokenize(src_lang, tgt_lang, sentence))
            target_prefix = self.get_target_prefixes(tgt_lang)
            if target_prefix:
                target_prefixes.append(target_prefix)

        results = self.model.translate_iterable(
            sentences_tokenized,
            target_prefix=target_prefixes if len(target_prefixes) else None,
            asynchronous=True,
            batch_type="tokens",
            max_batch_size=1024,
            beam_size=1,
            no_repeat_ngram_size=4,
        )
        for result in results:
            translated_sentence = self.detokenize(result.hypotheses[0][1:])
            translated_sentence = self.postprocess(tgt_lang, translated_sentence)
            translated_sentences.append(translated_sentence)

        return self.compose_text(sentences, translated_sentences)


class NLLBWikipediaTranslator(NLLBTranslator):
    MODEL = "nllb-wikipedia"

    def get_target_prefixes(self, tgt_lang: str):
        return None

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        target = "__" + languages.get_wikicode_to_iso(tgt_lang) + "__"
        return [target] + self.tokenizer.encode(content, out_type=str) + ["</s>"]
