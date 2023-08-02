import sys
from argparse import ArgumentParser, FileType

from translator import JSONTranslator, PlainTextTranslator
from translator.models import ModelConfig

if __name__ == "__main__":
    parser = ArgumentParser(prog="mint", description="Translate text between any languages")
    parser.add_argument("source")
    parser.add_argument("target")
    parser.add_argument("format", default="text", choices=["text", "json"])
    parser.add_argument(
        "file",
        type=FileType("r"),
        nargs="?",
        default=sys.stdin,
        help="File to read, if empty, stdin is used",
    )
    args = parser.parse_args()

    config = ModelConfig()
    if args.format == "json":
        translator = JSONTranslator(config, args.source, args.target)
    else:
        # Fallback, default
        translator = PlainTextTranslator(config, args.source, args.target)
    content = args.file.read()
    translation = translator.translate(content)
    print(translation)
