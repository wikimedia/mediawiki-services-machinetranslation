from collections import OrderedDict
from flask import Flask, jsonify, render_template, request, abort
import yaml
import time
import os
import statsd
import logging
import logging.config
from translator import TranslatorFactory, TranslatorConfig

logging.config.fileConfig("logging.conf")


os.chdir(os.path.dirname(os.path.realpath(__file__)))

statsd_host = "statsd.eqiad.wmnet"
statsd_client = None
try:
    statsd_client = statsd.StatsClient(statsd_host)
except Exception:
    logging.warning(f"Could not connect to statsd host {statsd_host}")

APP_NAME = "MachineTranslation"

app = Flask(__name__)
config = TranslatorConfig()


def get_languages() -> dict:
    return config.get_all_languages()


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
    test_from = "en"
    test_to = "ig"
    translator = TranslatorFactory(config, test_from, test_to)
    translation = translator.translate(test_from, test_to, ["health"])
    return "" if len(translation) and len(translation[0]) else False


@app.route("/api/translate/<source_lang>/<target_lang>", methods=["POST"])
def translate_handler(source_lang, target_lang):
    text = request.json.get("text")
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
    translator = TranslatorFactory(config, source_lang, target_lang)

    if not translator:
        abort(400, description="Could not find translator for the given language pair.")

    translated_text_lines = translator.translate(source_lang, target_lang, sentences)
    end = time.time()
    translationtime = end - start
    if statsd_client:
        statsd_client.incr(f"{APP_NAME.lower()}.mt.{source_lang}.{target_lang}")
        statsd_client.timing(f"{APP_NAME.lower()}.mt.timing", translationtime)

    return jsonify(
        translation="\n".join(translated_text_lines),
        translationtime=translationtime,
        sourcelanguage=source_lang,
        targetlanguage=target_lang,
        model=translator.MODEL,
    )
