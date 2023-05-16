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
        "ary": "ary_Arab",
        "arz": "arz_Arab",
        "as": "asm_Beng",
        "ast": "ast_Latn",
        "awa": "awa_Deva",
        "ay": "ayr_Latn",
        "az": "azj_Latn",
        "azb": "azb_Arab",
        "ba": "bak_Cyrl",
        "ban": "ban_Latn",
        "be": "bel_Cyrl",
        "bem": "bem_Latn",
        "bg": "bul_Cyrl",
        "bh": "bho_Deva",
        "bjn": "bjn_Arab",
        "bjn": "bjn_Latn",
        "bm": "bam_Latn",
        "bn": "ben_Beng",
        "bo": "bod_Tibt",
        "bs": "bos_Latn",
        "bug": "bug_Latn",
        "ca": "cat_Latn",
        "ceb": "ceb_Latn",
        "cjk": "cjk_Latn",
        "ckb": "ckb_Arab",
        "crh": "crh_Latn",
        "cs": "ces_Latn",
        "cy": "cym_Latn",
        "da": "dan_Latn",
        "de": "deu_Latn",
        "din": "dik_Latn",
        "dyu": "dyu_Latn",
        "dz": "dzo_Tibt",
        "ee": "ewe_Latn",
        "el": "ell_Grek",
        "en": "eng_Latn",
        "eo": "epo_Latn",
        "es": "spa_Latn",
        "et": "est_Latn",
        "eu": "eus_Latn",
        "fa": "pes_Arab",
        "fa": "prs_Arab",
        "ff": "fuv_Latn",
        "fi": "fin_Latn",
        "fj": "fij_Latn",
        "fo": "fao_Latn",
        "fon": "fon_Latn",
        "fr": "fra_Latn",
        "fur": "fur_Latn",
        "ga": "gle_Latn",
        "gd": "gla_Latn",
        "gl": "glg_Latn",
        "gn": "grn_Latn",
        "gu": "guj_Gujr",
        "ha": "hau_Latn",
        "he": "heb_Hebr",
        "hi": "hin_Deva",
        "hne": "hne_Deva",
        "hr": "hrv_Latn",
        "ht": "hat_Latn",
        "hu": "hun_Latn",
        "hy": "hye_Armn",
        "id": "ind_Latn",
        "ig": "ibo_Latn",
        "ilo": "ilo_Latn",
        "is": "isl_Latn",
        "it": "ita_Latn",
        "ja": "jpn_Jpan",
        "jv": "jav_Latn",
        "kab": "kab_Latn",
        "kac": "kac_Latn",
        "ka": "kat_Geor",
        "kam": "kam_Latn",
        "kbp": "kbp_Latn",
        "kea": "kea_Latn",
        "kg": "kon_Latn",
        "ki": "kik_Latn",
        "kk": "kaz_Cyrl",
        "kmb": "kmb_Latn",
        "km": "khm_Khmr",
        "knc": "knc_Arab",
        "knc": "knc_Latn",
        "kn": "kan_Knda",
        "ko": "kor_Hang",
        "ks": "kas_Arab",
        "ku": "kmr_Latn",
        "ky": "kir_Cyrl",
        "lb": "ltz_Latn",
        "lg": "lug_Latn",
        "lij": "lij_Latn",
        "li": "lim_Latn",
        "lmo": "lmo_Latn",
        "ln": "lin_Latn",
        "lo": "lao_Laoo",
        "ltg": "ltg_Latn",
        "lt": "lit_Latn",
        "lua": "lua_Latn",
        "lu": "lus_Latn",
        "luo": "luo_Latn",
        "lvs": "lvs_Latn",
        "mag": "mag_Deva",
        "mai": "mai_Deva",
        "mg": "plt_Latn",
        "mi": "mri_Latn",
        "min": "min_Arab",
        "min": "min_Latn",
        "mk": "mkd_Cyrl",
        "ml": "mal_Mlym",
        "mni": "mni_Beng",
        "mn": "khk_Cyrl",
        "mos": "mos_Latn",
        "mr": "mar_Deva",
        "ms": "zsm_Latn",
        "mt": "mlt_Latn",
        "my": "mya_Mymr",
        "nb": "nob_Latn",
        "ne": "npi_Deva",
        "nl": "nld_Latn",
        "nn": "nno_Latn",
        "nso": "nso_Latn",
        "nus": "nus_Latn",
        "ny": "nya_Latn",
        "oc": "oci_Latn",
        "om": "gaz_Latn",
        "or": "ory_Orya",
        "pag": "pag_Latn",
        "pa": "pan_Guru",
        "pap": "pap_Latn",
        "pl": "pol_Latn",
        "ps": "pbt_Arab",
        "pt": "por_Latn",
        "qu": "quy_Latn",
        "rn": "run_Latn",
        "ro": "ron_Latn",
        "ru": "rus_Cyrl",
        "rw": "kin_Latn",
        "sa": "san_Deva",
        "sat": "sat_Beng",  # NLLB uses this language code even though the script in corpus is Ol Chiki
        "scn": "scn_Latn",
        "sc": "srd_Latn",
        "sd": "snd_Arab",
        "sg": "sag_Latn",
        "shn": "shn_Mymr",
        "si": "sin_Sinh",
        "sk": "slk_Latn",
        "sl": "slv_Latn",
        "sm": "smo_Latn",
        "sn": "sna_Latn",
        "so": "som_Latn",
        "sq": "als_Latn",
        "sr": "srp_Cyrl",
        "ss": "ssw_Latn",
        "st": "sot_Latn",
        "su": "sun_Latn",
        "sv": "swe_Latn",
        "sw": "swh_Latn",
        "szl": "szl_Latn",
        "taq": "taq_Latn",
        "taq": "taq_Tfng",
        "ta": "tam_Taml",
        "te": "tel_Telu",
        "tg": "tgk_Cyrl",
        "th": "tha_Thai",
        "ti": "tir_Ethi",
        "tk": "tuk_Latn",
        "tl": "tgl_Latn",
        "tn": "tsn_Latn",
        "tpi": "tpi_Latn",
        "tr": "tur_Latn",
        "ts": "tso_Latn",
        "tt": "tat_Cyrl",
        "tum": "tum_Latn",
        "tw": "twi_Latn",
        "tzm": "tzm_Tfng",
        "ug": "uig_Arab",
        "uk": "ukr_Cyrl",
        "umb": "umb_Latn",
        "ur": "urd_Arab",
        "uz": "uzn_Latn",
        "vec": "vec_Latn",
        "vi": "vie_Latn",
        "war": "war_Latn",
        "wo": "wol_Latn",
        "xh": "xho_Latn",
        "yi": "ydd_Hebr",
        "yo": "yor_Latn",
        "zh": "zho_Hans",
        "zh": "zho_Hant",
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
            repetition_penalty=2,
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
        target = "__" + self.WIKI2ISO[tgt_lang] + "__"
        return [target] + self.tokenizer.encode(content, out_type=str) + ["</s>" ]


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
