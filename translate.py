from collections import OrderedDict
from flask import Flask, jsonify, render_template, request
from pathlib import Path
from sentencepiece import SentencePieceProcessor
from typing import List
import ctranslate2
import json
import multiprocessing
import os
import time

os.chdir(os.path.dirname(os.path.realpath(__file__)))

app = Flask(
    __name__
)
model=None
tokenizer=None
config = json.loads(Path("config.json").read_text())

@app.route("/", defaults={"path": ""})
def index(path):
    languages= OrderedDict(sorted(config.get("languages").items(), key=lambda x: x[1]))
    return render_template("index.html", languages=languages)

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


@app.route("/api/translate", methods=["POST", "GET"])
def translate_handler():
    text = None
    source_lang = "en"
    target_lang = "ml"
    if request.method == "POST":
        text = request.json.get("text")
        source_lang = request.json.get("from")
        target_lang = request.json.get("to")
    else:
        text = request.args.get("text")
        source_lang = request.args.get("from")
        target_lang = request.args.get("to")
    src_text_lines = text.strip().splitlines()
    start = time.time()
    tgt_text_lines = translate(source_lang, target_lang, src_text_lines)
    end = time.time()
    return jsonify(
        translation='\n'.join(tgt_text_lines),
        translationtime = end-start
    )

def translate(src_lang, tgt_lang, sentences)->List[str]:
    """
    Translate the text from source lang to target lang
    """
    global model, tokenizer
    sentences_tokenized=[]
    translation=[]
    target_prefix=[]
    if not model:
        init()
    for sentence in sentences:
        sentences_tokenized.append(
                tokenizer.encode(sentence, out_type=str) + ['</s>', src_lang]
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

def getModel():
    return ctranslate2.Translator(
        config.get("model"), # Model
        # maximum number of batches executed in parallel.
        # => Increase this value to increase the throughput.
        inter_threads=multiprocessing.cpu_count(),
        #  number of OpenMP threads that is used per batch.
        # => Increase this value to decrease the latency on CPU.
        intra_threads=multiprocessing.cpu_count(),
        device="auto",
        compute_type='auto'
    )

def getTokenizer() ->SentencePieceProcessor:
    sp = SentencePieceProcessor()
    sp.load(config.get("tokenizer"))
    return sp

def init():
    global model, tokenizer
    model = getModel()
    tokenizer = getTokenizer()
    print("Translator initialized")

if __name__ == "__main__":
    init()

