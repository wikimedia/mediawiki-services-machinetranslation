import sys
from argparse import ArgumentParser, FileType
from enum import StrEnum

from translator import (
    TranslatorRegistry,
)
from translator.models import ModelConfiguration

if __name__ == "__main__":
    translatorDefs = TranslatorRegistry.get_translators()
    formats = [translatorDef.meta.format for translatorDef in translatorDefs]
    config = ModelConfiguration()
    FormatEnum = StrEnum("FormatEnum", dict(zip(formats, formats, strict=False)))
    ModelEnum = StrEnum(
        "ModelEnum", dict(zip(config.get_model_names(), config.get_model_names(), strict=False))
    )
    parser = ArgumentParser(prog="mint", description="Translate text between any languages")
    parser.add_argument("-s", "--source")
    parser.add_argument("-t", "--target", type=str)
    parser.add_argument("-m", "--model", type=ModelEnum, choices=ModelEnum)
    parser.add_argument(
        "-f", "--format", default=FormatEnum.text, type=FormatEnum, choices=FormatEnum
    )
    parser.add_argument(
        "-i",
        "--infile",
        type=FileType("r"),
        nargs="?",
        default=sys.stdin,
        help="File to read, if empty, stdin is used",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        type=FileType("w"),
        nargs="?",
        default=sys.stdout,
        help="File to write, if empty, stdout is used",
    )
    parser.add_argument("-u", "--url", help="URL if the translator accepts it", required=False)
    args = parser.parse_args()

    for format in formats:
        if format == args.format:
            translators = [
                translatorDef
                for translatorDef in translatorDefs
                if translatorDef.meta.format == format
            ]
            translator = translators[0](config, args.source, args.target, args.model)
            if args.url is not None:
                content = args.url
                print(content)
            else:
                content = args.infile.read()
            translation = translator.translate(content)
            args.outfile.write("=" * 80)
            args.outfile.write("\n" + translation + "\n")
