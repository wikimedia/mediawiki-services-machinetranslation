import logging
import logging.config
import os
import time
from enum import StrEnum
from typing import Optional

import statsd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from translator import TranslatorRegistry
from translator.models import ModelConfiguration, ModelFactory

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

app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="MinT Machine Translation service",
        version="1.0.0",
        summary="OpenAPI schema",
        description="""
MinT is a machine translation system hosted by Wikimedia Foundation.
It uses multiple Neural Machine translation models to provide translation
between large number of languages.
""",
        routes=app.routes,
    )
    # Cache the schema
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

config = ModelConfiguration()
translator_classes = TranslatorRegistry.get_translators()

formats = [translator_class.meta.format for translator_class in translator_classes]
ModelEnum = StrEnum("ModelEnum", dict(zip(config.get_model_names(), config.get_model_names())))
FormatEnum = StrEnum("FormatEnum", dict(zip(formats, formats)))


class TranslationRequest(BaseModel):
    format: FormatEnum = Field(..., description="The content format")
    content: str = Field(..., description="The content to translate")
    source_language: str = Field(..., description="The source language")
    target_language: str = Field(..., description="The target language")
    model: Optional[ModelEnum] = Field(None, description="The MT model to use")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "format": "text",
                    "content": "The Earth rotates around the Sun from west to east.",
                    "source_language": "en",
                    "target_language": "ta",
                },
            ]
        }
    }


class TranslationResponse(BaseModel):
    translation: str = Field(..., description="The translated content")
    translationtime: float = Field(..., description="Time taken for translation in seconds")
    sourcelanguage: str = Field(..., description="Source language code")
    targetlanguage: str = Field(..., description="Target language code")
    model: str = Field(..., description="Translator model used")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_languages() -> dict:
    return config.get_all_languages()


@app.middleware("statsd")
async def add_statsd_request_log(request: Request, call_next):
    if statsd_client:
        statsd_client.incr("requests")
    response = await call_next(request)
    return response


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "format": "text", "formats": formats, "languages": get_languages()},
    )


@app.get("/healthz")
async def health():
    test_from = "en"
    test_to = "ig"
    translator = ModelFactory(config, test_from, test_to)
    translation = translator.translate(test_from, test_to, ["health"])
    return "" if len(translation) and len(translation[0]) else False


@app.get("/{format}")
async def format_page(request: Request, format: str):
    if format in formats:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "format": format,
                "formats": formats,
                "languages": get_languages(),
            },
        )
    else:
        raise HTTPException(status_code=404)


@app.get("/api/languages")
async def list_languages():
    return get_languages()


@app.post("/api/translate")
async def translate_handler(request: TranslationRequest) -> TranslationResponse:
    translator_class = None
    translators = [
        translator_class
        for translator_class in translator_classes
        if translator_class.meta.format == request.format
    ]
    if translators:
        translator_class = translators[0]

    if not translator_class:
        raise HTTPException(
            status_code=413,
            detail="No translator found for the passed content",
        )

    char_limit = translator_class.meta.character_limit
    if len(request.content) > char_limit:
        raise HTTPException(
            status_code=413,
            detail=f"Request size exceeds maximum character limit {char_limit}",
        )

    translator = translator_class(
        config, request.source_language, request.target_language, request.model
    )
    start = time.time()
    translation = translator.translate(request.content)
    end = time.time()
    translationtime = end - start
    if statsd_client:
        statsd_client.incr(f"mt.{request.source_language}.{request.target_language}")
        statsd_client.timing("mt.timing", int(translationtime * 1000))

    response = TranslationResponse(
        translation=translation,
        translationtime=translationtime,
        sourcelanguage=request.source_language,
        targetlanguage=request.target_language,
        model=translator.model_name,
    )
    return response


@app.post("/api/translate/{source_lang}/{target_lang}")
async def translate_handler_deprecated(
    source_lang, target_lang, request: Request
) -> TranslationResponse:
    content = None
    request_dict = await request.json()

    for format in formats:
        if format in request_dict:
            content = request_dict.get(format)
            break

    translation_request = TranslationRequest(
        format=format, source_language=source_lang, target_language=target_lang, content=content
    )

    return await translate_handler(translation_request)
