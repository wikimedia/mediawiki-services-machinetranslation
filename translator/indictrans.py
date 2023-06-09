import logging
import logging.config
from typing import List

from indicnlp.transliterate import unicode_transliterate

from translator import BaseTranslator, languages

logging.config.fileConfig("logging.conf")


class IndicTransTranslator(BaseTranslator):
    MODEL = "indictrans2-en-indic"

    def __init__(self, config):
        super().__init__(config)
        self.transliterator = unicode_transliterate.UnicodeIndicTransliterator()

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        return [
            languages.get_wikicode_from_nllb(src_lang),
            languages.get_wikicode_from_nllb(tgt_lang),
        ] + self.tokenizer.encode(content, out_type=str)

    def detokenize(self, content: List[str]) -> str:
        return "".join(content).replace("▁", " ").strip()

    def transliterate_to_devanagari(self, sentence: str, src_lang) -> str:
        return self.transliterator.transliterate(sentence, src_lang, "hi").replace(" ् ", "्")

    def transliterate_from_devanagari(self, sentence: str, tgt_lang) -> str:
        return self.transliterator.transliterate(sentence, "hi", tgt_lang)

    def translate(self, src_lang: str, tgt_lang: str, sentences: List[str]) -> List[str]:
        """
        Translate the text from source lang to target lang
        """
        translation: List[str] = []
        sentences_tokenized: List[str] = []

        for sentence in sentences:
            sentence = self.preprocess(src_lang, sentence)
            if src_lang != "en":
                sentence = self.transliterate_to_devanagari(sentence, src_lang)
            sentences_tokenized.append(self.tokenize(src_lang, tgt_lang, sentence))
        results = self.model.translate_iterable(
            sentences_tokenized,
            asynchronous=True,
            batch_type="tokens",
            max_batch_size=1024,
            beam_size=1,
            no_repeat_ngram_size=4,
        )
        for result in results:
            translated_sentence = self.detokenize(result.hypotheses[0])

            if tgt_lang != "en":
                translated_sentence = self.transliterate_from_devanagari(
                    translated_sentence, tgt_lang
                )

            translated_sentence = translated_sentence.replace(" .", ".")
            translated_sentence = self.postprocess(tgt_lang, translated_sentence)
            translation.append(translated_sentence)
        return translation


class IndicEnTransTranslator(IndicTransTranslator):
    MODEL = "indictrans2-indic-en"


class EnIndicTransTranslator(IndicTransTranslator):
    MODEL = "indictrans2-en-indic"
