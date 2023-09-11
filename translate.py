import logging
import logging.config
import os
import time

import pycld2 as cld2
import statsd
import yaml
from flask import Flask, abort, jsonify, render_template, request

from translator import TranslatorRegistry
from translator.models import ModelConfig, ModelFactory

logging.config.fileConfig("logging.conf")

os.chdir(os.path.dirname(os.path.realpath(__file__)))

APP_NAME = "MachineTranslation"

statsd_host = os.getenv("STATSD_HOST", "localhost")
statsd_port = int(os.getenv("STATSD_PORT", 8125))
statsd_prefix = os.getenv("STATSD_PREFIX", "machinetranslation")

statsd_client = None
try:
    statsd_client = statsd.StatsClient(statsd_host, port=statsd_port, prefix=statsd_prefix)
except Exception:
    logging.warning(f"Could not connect to statsd host {statsd_host}:{statsd_port}")


app = Flask(__name__)
config = ModelConfig()
translator_classes = TranslatorRegistry.get_translators()
# Supported formats
formats = [translator_class.meta.format for translator_class in translator_classes]


def get_languages() -> dict:
    return config.get_all_languages()


@app.route("/")
def index():
    return render_template("index.html", format="text", formats=formats, languages=get_languages())


@app.route("/<string:format>")
def format_page(format: str):
    if format in formats:
        return render_template(
            "index.html", format=format, formats=formats, languages=get_languages()
        )
    else:
        abort(404)


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
    translator = ModelFactory(config, test_from, test_to)
    translation = translator.translate(test_from, test_to, ["health"])
    return "" if len(translation) and len(translation[0]) else False


@app.route("/api/translate/<source_lang>/<target_lang>", methods=["POST"])
def translate_handler(source_lang, target_lang):
    content = None
    translator_class = None
    for format in formats:
        if format in request.json:
            translators = [
                translator_class
                for translator_class in translator_classes
                if translator_class.meta.format == format
            ]
            if len(translators):
                translator_class = translators[0]
                content = request.json.get(format)
                break
    if not translator_class:
        abort(
            413,
            description="No translator found for the passed content",
        )

    char_limit = translator_class.meta.character_limit
    if len(content) > char_limit:
        abort(
            413,  # Request Entity Too Large
            description=f"Request size exceeds maximum character limit {char_limit}",
        )

    translator = translator_class(config, source_lang, target_lang)
    start = time.time()
    translation = translator.translate(content)
    end = time.time()
    translationtime = end - start
    if statsd_client:
        statsd_client.incr(f"mt.{source_lang}.{target_lang}")
        statsd_client.timing("mt.timing", int(translationtime * 1000))

    return jsonify(
        translation=translation,
        translationtime=translationtime,
        sourcelanguage=source_lang,
        targetlanguage=target_lang,
        model=translator.model_name,
    )


@app.route("/api/detectlang", methods=["POST"])
def detect_language():
    text = request.json.get("text")
    reliable, index, top_3_choices = cld2.detect(text, returnVectors=False, bestEffort=False)
    if not reliable:
        abort(413, "Try passing a longer snippet of text")
    return jsonify(
        language=top_3_choices[0][1],
        score=top_3_choices[0][2],
    )
