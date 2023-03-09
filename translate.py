from collections import OrderedDict
from flask import Flask, jsonify, render_template, request, abort
from pathlib import Path
from sentencepiece import SentencePieceProcessor
from typing import List
from ctranslate2 import Translator
import json
import yaml
import multiprocessing
import os
import time
import statsd
import logging
import logging.config

logging.config.fileConfig("logging.conf")


os.chdir(os.path.dirname(os.path.realpath(__file__)))

statsd_host = "statsd.eqiad.wmnet"
statsd_client = None
try:
    statsd_client = statsd.StatsClient(statsd_host)
except Exception:
    logging.error(f"Could not connect to statsd host {statsd_host}")

APP_NAME = "MachineTranslation"

app = Flask(__name__)


model = None
tokenizer = None
config = json.loads(Path("config.json").read_text())


def get_languages() -> dict:
    return OrderedDict(sorted(config.get("languages").items(), key=lambda x: x[1]))


@app.route("/", defaults={"path": ""})
def index(path):
    return render_template("index.html", languages=get_languages())


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response


@app.route("/api/spec")
def show_spec():
    with open("spec.yaml", "r") as file:
        spec = yaml.safe_load(file)
    return jsonify(spec)


@app.route("/api/languages")
def list_languages():
    return get_languages()


@app.route("/healthz")
def health():
    translation = translate("eng_Latn", "ibo_Latn", ["health"])
    return "" if len(translation) and len(translation[0]) else False


@app.route("/api/translate/<source_lang>/<target_lang>", methods=["POST"])
def translate_handler(source_lang, target_lang):
    text = request.json.get("text")
    supported_languages = get_languages()

    if not source_lang in supported_languages:
        abort(400, description="Invalid source language.")
    if not target_lang in supported_languages:
        abort(400, description="Invalid target language.")

    if len(text) > 10000:
        abort(
            413,
            description="Request too large to handle. Maximum 10000 characters are supported.",
        )
    sentences = text.strip().splitlines()
    if len(sentences) > 25:
        abort(
            413,
            description="Request too large to handle. Maximum 25 sentences are supported.",
        )
    start = time.time()
    tgt_text_lines = translate(source_lang, target_lang, sentences)
    end = time.time()
    translationtime=end - start
    if statsd_client:
        statsd_client.incr(f'{APP_NAME.lower()}.mt.{source_lang}.{target_lang}')
        statsd_client.timing(f'{APP_NAME.lower()}.mt.timing', translationtime)

    return jsonify(translation="\n".join(tgt_text_lines),translationtime=translationtime)


def translate(src_lang, tgt_lang, sentences) -> List[str]:
    """
    Translate the text from source lang to target lang
    """
    global model, tokenizer
    sentences_tokenized = []
    translation = []
    target_prefix = []
    if not model:
        init()
    for sentence in sentences:
        sentences_tokenized.append(
            tokenizer.encode(sentence, out_type=str) + ["</s>", src_lang]
        )
        target_prefix.append([tgt_lang])

    results = model.translate_iterable(
        sentences_tokenized,
        target_prefix=target_prefix,
        asynchronous=True,
        batch_type="tokens",
        max_batch_size=1024,
        beam_size=1,
    )
    for result in results:
        translation.append(tokenizer.decode(result.hypotheses[0][1:]))
    return translation


def getModel() -> Translator:
    return Translator(
        config.get("model"),  # Model
        # maximum number of batches executed in parallel.
        # => Increase this value to increase the throughput.
        inter_threads=multiprocessing.cpu_count(),
        #  number of OpenMP threads that is used per batch.
        # => Increase this value to decrease the latency on CPU.
        intra_threads=multiprocessing.cpu_count(),
        device="auto",
        compute_type="auto",
    )


def getTokenizer() -> SentencePieceProcessor:
    sp = SentencePieceProcessor()
    sp.load(config.get("tokenizer"))
    return sp


def init():
    global model, tokenizer
    model = getModel()
    tokenizer = getTokenizer()
    logging.info("Translator initialized")


if __name__ == "__main__":
    init()

