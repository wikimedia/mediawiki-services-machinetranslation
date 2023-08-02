import fileinput
from argparse import ArgumentParser

from translator.segmenter import segment

if __name__ == "__main__":
    parser = ArgumentParser(prog="segmenter", description="Split the text to sentences")
    parser.add_argument("language")
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        help="Files to read, if empty, stdin is used",
    )
    args = parser.parse_args()
    sentences = []
    for text in fileinput.input(files=args.files):
        sentences += segment(args.language, text)

    print(sentences)
