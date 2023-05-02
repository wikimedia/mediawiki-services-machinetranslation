import multiprocessing
import logging
from pathlib import Path
from typing import List
import logging.config
from translator.base import BaseTranslator

logging.config.fileConfig("logging.conf")

class NLLBTranslator(BaseTranslator):
    MODEL = "nllb200-600M"
    WIKI2NLLBCODES = {
        "ace": "ace_Latn",
        "acm": "acm_Arab",
        "acq": "acq_Arab",
        "aeb": "aeb_Arab",
        "af": "afr_Latn",
        "ajp": "ajp_Arab",
        "ak": "aka_Latn",
        "am": "amh_Ethi",
        "ar": "arb_Arab",
        "as": "asm_Beng",
        "ast": "ast_Latn",
        "awa": "awa_Deva",
        "ayr": "ayr_Latn",
        "azb": "azb_Arab",
        "azj": "azj_Latn",
        "ba": "bak_Cyrl",
        "bm": "bam_Latn",
        "ban": "ban_Latn",
        "be": "bel_Cyrl",
        "bem": "bem_Latn",
        "bn": "ben_Beng",
        "bho": "bho_Deva",
        "bjn": "bjn_Arab",
        "bjn": "bjn_Latn",
        "bo": "bod_Tibt",
        "bs": "bos_Latn",
        "bug": "bug_Latn",
        "bg": "bul_Cyrl",
        "ca": "cat_Latn",
        "ceb": "ceb_Latn",
        "cs": "ces_Latn",
        "cjk": "cjk_Latn",
        "ckb": "ckb_Arab",
        "crh": "crh_Latn",
        "cy": "cym_Latn",
        "da": "dan_Latn",
        "de": "deu_Latn",
        "dik": "dik_Latn",
        "dyu": "dyu_Latn",
        "dz": "dzo_Tibt",
        "el": "ell_Grek",
        "en": "eng_Latn",
        "eo": "epo_Latn",
        "et": "est_Latn",
        "eu": "eus_Latn",
        "ee": "ewe_Latn",
        "fo": "fao_Latn",
        "fj": "fij_Latn",
        "fi": "fin_Latn",
        "fon": "fon_Latn",
        "fr": "fra_Latn",
        "fur": "fur_Latn",
        "fuv": "fuv_Latn",
        "gd": "gla_Latn",
        "ga": "gle_Latn",
        "gl": "glg_Latn",
        "gn": "grn_Latn",
        "gu": "guj_Gujr",
        "ht": "hat_Latn",
        "ha": "hau_Latn",
        "he": "heb_Hebr",
        "hi": "hin_Deva",
        "hne": "hne_Deva",
        "hr": "hrv_Latn",
        "hu": "hun_Latn",
        "hy": "hye_Armn",
        "ig": "ibo_Latn",
        "ilo": "ilo_Latn",
        "id": "ind_Latn",
        "is": "isl_Latn",
        "it": "ita_Latn",
        "jv": "jav_Latn",
        "ja": "jpn_Jpan",
        "kab": "kab_Latn",
        "kac": "kac_Latn",
        "kam": "kam_Latn",
        "kn": "kan_Knda",
        "ks": "kas_Arab",
        "ka": "kat_Geor",
        "knc": "knc_Arab",
        "knc": "knc_Latn",
        "kk": "kaz_Cyrl",
        "kbp": "kbp_Latn",
        "kea": "kea_Latn",
        "km": "khm_Khmr",
        "ki": "kik_Latn",
        "rw": "kin_Latn",
        "ky": "kir_Cyrl",
        "kmb": "kmb_Latn",
        "kmr": "kmr_Latn",
        "kg": "kon_Latn",
        "ko": "kor_Hang",
        "lo": "lao_Laoo",
        "lij": "lij_Latn",
        "li": "lim_Latn",
        "ln": "lin_Latn",
        "lt": "lit_Latn",
        "lmo": "lmo_Latn",
        "ltg": "ltg_Latn",
        "lb": "ltz_Latn",
        "lua": "lua_Latn",
        "lg": "lug_Latn",
        "luo": "luo_Latn",
        "lus": "lus_Latn",
        "lvs": "lvs_Latn",
        "mag": "mag_Deva",
        "mai": "mai_Deva",
        "ml": "mal_Mlym",
        "mr": "mar_Deva",
        "min": "min_Arab",
        "min": "min_Latn",
        "mk": "mkd_Cyrl",
        "plt": "plt_Latn",
        "mt": "mlt_Latn",
        "mni": "mni_Beng",
        "khk": "khk_Cyrl",
        "mos": "mos_Latn",
        "mi": "mri_Latn",
        "my": "mya_Mymr",
        "nl": "nld_Latn",
        "nn": "nno_Latn",
        "nb": "nob_Latn",
        "npi": "npi_Deva",
        "nso": "nso_Latn",
        "nus": "nus_Latn",
        "ny": "nya_Latn",
        "oc": "oci_Latn",
        "gaz": "gaz_Latn",
        "ory": "ory_Orya",
        "pag": "pag_Latn",
        "pa": "pan_Guru",
        "pap": "pap_Latn",
        "pes": "pes_Arab",
        "pl": "pol_Latn",
        "pt": "por_Latn",
        "fa": "prs_Arab",
        "pbt": "pbt_Arab",
        "quy": "quy_Latn",
        "ro": "ron_Latn",
        "rn": "run_Latn",
        "ru": "rus_Cyrl",
        "sg": "sag_Latn",
        "sa": "san_Deva",
        "sat": "sat_Olck",
        "scn": "scn_Latn",
        "shn": "shn_Mymr",
        "si": "sin_Sinh",
        "sk": "slk_Latn",
        "sl": "slv_Latn",
        "sm": "smo_Latn",
        "sn": "sna_Latn",
        "sd": "snd_Arab",
        "so": "som_Latn",
        "st": "sot_Latn",
        "es": "spa_Latn",
        "als": "als_Latn",
        "sc": "srd_Latn",
        "sr": "srp_Cyrl",
        "ss": "ssw_Latn",
        "su": "sun_Latn",
        "sv": "swe_Latn",
        "swh": "swh_Latn",
        "szl": "szl_Latn",
        "ta": "tam_Taml",
        "tt": "tat_Cyrl",
        "te": "tel_Telu",
        "tg": "tgk_Cyrl",
        "fil": "tgl_Latn",
        "th": "tha_Thai",
        "ti": "tir_Ethi",
        "taq": "taq_Latn",
        "taq": "taq_Tfng",
        "tpi": "tpi_Latn",
        "tn": "tsn_Latn",
        "ts": "tso_Latn",
        "tk": "tuk_Latn",
        "tum": "tum_Latn",
        "tr": "tur_Latn",
        "tw": "twi_Latn",
        "tzm": "tzm_Tfng",
        "ug": "uig_Arab",
        "uk": "ukr_Cyrl",
        "umb": "umb_Latn",
        "ur": "urd_Arab",
        "uzn": "uzn_Latn",
        "vec": "vec_Latn",
        "vi": "vie_Latn",
        "war": "war_Latn",
        "wo": "wol_Latn",
        "xh": "xho_Latn",
        "ydd": "ydd_Hebr",
        "yo": "yor_Latn",
        "zh": "zho_Hans",
        "zh": "zho_Hant",
        "zsm": "zsm_Latn",
        "zu": "zul_Latn",
    }

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        return self.tokenizer.encode(content, out_type=str) + ["</s>", self.WIKI2NLLBCODES[src_lang]]

    def detokenize(self, content: str) -> str:
        return self.tokenizer.decode(content)

    def get_target_prefixes(self, tgt_lang: str):
        return [self.WIKI2NLLBCODES[tgt_lang]]

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
        )
        for result in results:
            translation.append(self.detokenize(result.hypotheses[0][1:]))
        return translation


class NLLBWikipediaTranslator(NLLBTranslator):
    MODEL = "nllb-wikipedia"
    WIKI2ISO = {
        "as": "asm",  # Assamese
        "ast": "ast",  # Asturian
        "ay": "ayr",  # Central Aymara
        "ba": "bak",  # Bashkir
        "bem": "bem",  # Bemba
        "ca": "cat",  # Catalan
        "ckb": "ckb",  # Central Kurdish
        "en": "eng",  # English
        "fr": "fra",  # French
        "ha": "hau",  # Hausa
        "ig": "ibo",  # Igbo
        "ilo": "ilo",  # Iloko
        "is": "isl",  # Icelandic
        "kg": "kon",  # Kongo
        "ln": "lin",  # Lingala
        "lg": "lug",  # Ganda
        "nso": "nso",  # Norther Sotho
        "oc": "oci",  # Occitan
        "om": "orm",  # Oromo
        "pt": "por",  # Portuguese
        "ss": "ssw",  # Swati
        "qu": "que",  # Quechua
        "ru": "rus",  # Russian
        "es": "spa",  # Spanish
        "ss": "ssw",  # Swati
        "ti": "tir",  # Tigrinya
        "tn": "tsn",  # Tswana
        "ts": "tso",  # Tswana
        "wo": "wol",  # Wolof
        "zh-yue": "yue",  # Yue Chinese
        "yue": "yue",
        "zh": "zho_Hans",  # Chinese
        "zu": "zul",  # Zulu
    }

    def get_target_prefixes(self, tgt_lang: str):
        return None

    def tokenize(self, src_lang: str, tgt_lang: str, content):
        src = "__" + self.WIKI2ISO[src_lang] + "__"
        target = "__" + self.WIKI2ISO[tgt_lang] + "__"
        return [target] + self.tokenizer.encode(content, out_type=str) + ["</s>", src]


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
        NLLBWikipediaTranslator(models[NLLBWikipediaTranslator.MODEL]).translate(
            "en", "ig", sentences
        )
    )
