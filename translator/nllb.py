import logging
from typing import List
import logging.config
from translator import BaseTranslator
from translator import languages

logging.config.fileConfig("logging.conf")


class NLLBTranslator(BaseTranslator):
    MODEL = "nllb200-600M"

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        return self.tokenizer.encode(content, out_type=str) + ["</s>", languages.get_wikicode_from_nllb(src_lang)]

    def detokenize(self, content: str) -> str:
        return self.tokenizer.decode(content)

    def get_target_prefixes(self, tgt_lang: str):
        return [languages.get_wikicode_from_nllb(tgt_lang)]

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

        results = self.model.translate_iterable(
            sentences_tokenized,
            target_prefix=target_prefixes if len(target_prefixes) else None,
            asynchronous=True,
            batch_type="tokens",
            max_batch_size=1024,
            beam_size=1,
            repetition_penalty=2,
        )
        for result in results:
            translation.append(self.detokenize(result.hypotheses[0][1:]))
        return translation


class NLLBWikipediaTranslator(NLLBTranslator):
    MODEL = "nllb-wikipedia"

    def get_target_prefixes(self, tgt_lang: str):
        return None

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        target = "__" + languages.get_wikicode_to_iso(tgt_lang) + "__"
        return [target] + self.tokenizer.encode(content, out_type=str) + ["</s>"]


sentences = """
Jazz is a music genre that originated in the African-American communities of New Orleans, Louisiana, United States, in the late 19th and early 20th centuries, with its roots in blues and ragtime.
Since the 1920s Jazz Age, it has been recognized as a major form of musical expression in traditional and popular music, linked by the common bonds of African-American and European-American musical parentage.
Jazz is characterized by swing and blue notes, complex chords, call and response vocals, polyrhythms and improvisation.
Jazz has roots in West African cultural and musical expression, and in African-American music traditions.
""".strip().splitlines()

if __name__ == "__main__":
    import yaml
    import time

    with open("./models.yaml") as f:
        models = yaml.load(f, Loader=yaml.SafeLoader)

    translator=NLLBWikipediaTranslator(models[NLLBWikipediaTranslator.MODEL])
    start = time.time()
    print(translator.translate("en", "ig", sentences))
    end = time.time()
    print(f"Translated in {end-start} seconds")
