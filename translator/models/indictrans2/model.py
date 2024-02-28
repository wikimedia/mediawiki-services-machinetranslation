import logging
import logging.config
from typing import Dict, List

from translator.models import BaseModel, languages
from translator.models.utils import apply_missing_references, extract_potential_references

from .utils import postprocess_batch, preprocess_batch

logging.config.fileConfig("logging.conf")


class IndicTransModel(BaseModel):
    MODEL = "indictrans2-indic-indic"

    def __init__(self, config):
        super().__init__(config)

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        return [
            languages.get_wikicode_from_nllb(src_lang),
            languages.get_wikicode_from_nllb(tgt_lang),
        ] + self.tokenizer.encode(content, out_type=str)

    def detokenize(self, content: List[str]) -> str:
        return "".join(content).replace("▁", " ").strip()

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

        sentences_tokenized: List[str] = []
        translated_sentences: List[str] = []
        placeholder_entity_map_sents: Dict[str, str] = {}
        reference_map: Dict[str, List[str]] = {}

        for sentence in sentences:
            reference_map[sentence] = extract_potential_references(sentence)

        pre_processed_sentences, placeholder_entity_map_sents = preprocess_batch(
            sentences, languages.get_wikicode_from_nllb(src_lang)
        )

        for sentence in pre_processed_sentences:
            sentence = self.preprocess(src_lang, sentence)
            sentences_tokenized.append(self.tokenize(src_lang, tgt_lang, sentence))

        results = self.model.translate_iterable(
            sentences_tokenized,
            asynchronous=True,
            batch_type="tokens",
            max_batch_size=1024,
            beam_size=1,
            no_repeat_ngram_size=4,
        )

        translated_sentences: List[str] = [
            self.detokenize(result.hypotheses[0]) for result in results
        ]

        translated_sentences = apply_missing_references(reference_map, translated_sentences)

        translated_sentences = postprocess_batch(
            translated_sentences,
            placeholder_entity_map_sents,
            languages.get_wikicode_from_nllb(tgt_lang),
        )

        return [self.postprocess(tgt_lang, sentence) for sentence in translated_sentences]


class IndicEnTransModel(IndicTransModel):
    MODEL = "indictrans2-indic-en"


class EnIndicTransModel(IndicTransModel):
    MODEL = "indictrans2-en-indic"
