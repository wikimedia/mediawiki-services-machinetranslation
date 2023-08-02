import fileinput
from argparse import ArgumentParser

from translator.models import ModelConfig, ModelFactory

if __name__ == "__main__":
    parser = ArgumentParser(prog="mint", description="Translate text between any languages")
    parser.add_argument("source")
    parser.add_argument("target")
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        help="Files to read, if empty, stdin is used",
    )
    args = parser.parse_args()

    config = ModelConfig()
    translator = ModelFactory(config, args.source, args.target)
    for text in fileinput.input(files=args.files):
        translation = translator.translate(args.source, args.target, text)
        print(translation)
