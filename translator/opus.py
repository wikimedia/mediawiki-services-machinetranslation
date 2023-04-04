import logging
from pathlib import Path
from typing import List
import logging.config
from translator.base import BaseTranslator

logging.config.fileConfig("logging.conf")

class OpusTranslator(BaseTranslator):
    MODEL = "opusmt"

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        return self.tokenizer.encode(content, out_type=str)

    def detokenize(self, content: str) -> str:
        return self.tokenizer.decode(content).replace('▁',' ').strip()

    def translate(
        self, src_lang: str, tgt_lang: str, sentences: List[str]
    ) -> List[str]:
        """
        Translate the text from source lang to target lang
        """
        translation:List[str]= []
        sentences_tokenized:List[str] = []

        for sentence in sentences:
            sentences_tokenized.append(self.tokenize(src_lang, tgt_lang, sentence))

        results = self.model.translate_iterable(
            sentences_tokenized,
            asynchronous=True,
            batch_type="tokens",
            max_batch_size=1024,
            beam_size=1,
        )

        for result in results:
            translation.append(self.detokenize(result.hypotheses[0][1:]))
        return translation

sentences = """
Jazz is a music genre that originated in the African-American communities of New Orleans, Louisiana, United States, in the late 19th and early 20th centuries, with its roots in blues and ragtime.
Since the 1920s Jazz Age, it has been recognized as a major form of musical expression in traditional and popular music, linked by the common bonds of African-American and European-American musical parentage.
Jazz is characterized by swing and blue notes, complex chords, call and response vocals, polyrhythms and improvisation.
Jazz has roots in West African cultural and musical expression, and in African-American music traditions.
""".strip().splitlines()

if __name__ == "__main__":
    import yaml

    with open("./models.yaml") as f:
        models = yaml.load(f, Loader=yaml.SafeLoader)
    print(
        OpusTranslator(models[OpusTranslator.MODEL]).translate(
            "en", "bcl", sentences
        )
    )
