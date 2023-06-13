import logging
from typing import List
import logging.config
from translator import BaseTranslator
from indicnlp.transliterate import unicode_transliterate
from translator import languages

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

    def translate(
        self, src_lang: str, tgt_lang: str, sentences: List[str]
    ) -> List[str]:
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


if __name__ == "__main__":
    import yaml

    sentences = {
        "en": """
    All plants, animals, and fungi need oxygen for cellular respiration, which extracts energy by the reaction of oxygen with molecules derived from food and produces carbon dioxide as a waste product.
    """,
        "ml": """
    കേരളത്തിൽ സാധാരണ കണ്ടുവരുന്ന ഒരു പക്ഷിയാണ് ആറ്റകുരുവി.
    കൂരിയാറ്റ, തൂക്കണാംകുരുവി എന്നീ പേരുകളിലും ഇത് അറിയപ്പെടുന്നു.
    ഇത് അങ്ങാടിക്കുരുവിയോട് വളരെയധികം സാദൃശ്യമുള്ള പക്ഷിയാണ്.
    അങ്ങാടിക്കുരുവിയുടെ വലിപ്പം ഉള്ള ഈ പക്ഷി പൊതുവേ വയലുകൾക്ക് സമീപമാണ് കാണപ്പെടുന്നത്.
    പ്രജനനകാലത്തൊഴിച്ച് കിളികളിൽ ആണും പെണ്ണും തമ്മിൽ നിറവ്യത്യാസങ്ങൾ ഇല്ല.
    വയലുകളോട് ചേർന്നുനിൽക്കുന്ന ഉയരമുള്ള മരങ്ങളിൽ നെല്ലോല കൊണ്ട് നെയ്തെടുക്കുന്ന നീളവും ഉറപ്പും ഏറിയ കൂടുകളാണ് ഈ പക്ഷിയുടെ പ്രത്യേകത.
    തൂക്കണാം കുരുവികൾ ശരിക്കും ഒന്നിലധികം ഇണകളെ സ്വീകരിക്കുന്ന പക്ഷിയാണ്‌.
    കുരുവിയുടെ ആ മനോഹരമായ കൂട് നിർമിക്കുന്നത് ആൺപക്ഷിയാണ്.
    """,
    }

    with open("./models.yaml") as f:
        models = yaml.load(f, Loader=yaml.SafeLoader)
    print(
        EnIndicTransTranslator(models[EnIndicTransTranslator.MODEL]).translate(
            "en", "ml", sentences["en"].strip().splitlines()
        )
    )
    print(
        IndicEnTransTranslator(models[IndicEnTransTranslator.MODEL]).translate(
            "ml", "en", sentences["ml"].strip().splitlines()
        )
    )
