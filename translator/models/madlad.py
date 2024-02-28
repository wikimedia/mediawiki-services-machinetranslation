import logging
import logging.config
from typing import Dict, List

from translator.models import BaseModel, languages
from translator.models.utils import apply_missing_references, extract_potential_references

logging.config.fileConfig("logging.conf")


class MADLAD400Model(BaseModel):
    MODEL = "madlad-400"

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        return self.tokenizer.encode(f"<2{tgt_lang}> {content}", out_type=str)

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
        src_lang = languages.WIKI2MADLAD.get(src_lang, src_lang)
        tgt_lang = languages.WIKI2MADLAD.get(tgt_lang, tgt_lang)
        translated_sentences: List[str] = []
        sentences_tokenized: List[str] = []
        reference_map: Dict[str, List[str]] = {}

        for sentence in sentences:
            reference_map[sentence] = extract_potential_references(sentence)
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

        translated_sentences = apply_missing_references(reference_map, translated_sentences)

        return translated_sentences
