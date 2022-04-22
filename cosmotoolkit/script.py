import argparse
import logging
import sys
from pathlib import Path
from PIL import Image


class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt: str = "%(levelname)8s: %(message)s"):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class CoverNameSpace(argparse.Namespace):
    file: str
    output: str
    force: bool
    extension: str


def run_cover(args: CoverNameSpace, logger):
    try:
        with Image.open(args.file) as image:
            image.convert('RGB')
    except OSError:
        logger.error(f"{args.file} is not a valid image file")
        sys.exit(1)

    width, height = image.size
    ratio = width / height
    cwidth, cheight = 1146 / width, 717 / height
    if cwidth > cheight:
        newsize = (int(width * cwidth), int(width * cwidth / ratio))
    else:
        newsize = (int(height * cheight * ratio), int(height * cheight))
    image = image.resize(newsize, Image.LANCZOS)

    output = Path(args.output)
    if output.exists() and not args.force:
        logger.error("%s already exists", output)
        sys.exit(1)
    image.save(args.output, args.extension)


def run_sub(args, logger):
    pass


def main():
    parser = argparse.ArgumentParser(description='cosmotoolkit')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
        description="available subcommands",
    )

    cover_parser = subparsers.add_parser("cover", help="process cover image")
    cover_parser.add_argument("file", help="input file path")
    cover_parser.add_argument(
        "-o", "--output", help="output file path", default="cover.jpg")
    cover_parser.add_argument(
        "-f", "--force", help="force overwrite", action="store_true")
    cover_parser.add_argument(
        "-ext", "--extension", help="output file extension", default="jpeg")

    sub_parser = subparsers.add_parser("sub", help="process subtitles")
    sub_parser.add_argument("file", help="input file path")
    sub_parser.add_argument(
        "-o", "--output", help="output file path", default="sub.ass")

    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(CustomFormatter())
    if args.verbose == 0:
        logger.setLevel(logging.WARNING)
        stdout_handler.setLevel(logging.WARNING)
    elif args.verbose == 1:
        logger.setLevel(logging.INFO)
        stdout_handler.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)
        stdout_handler.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)

    if args.subcommand == "cover":
        run_cover(args, logger)  # type: ignore
    elif args.subcommand == "sub":
        run_sub(args, logger)  # type: ignore
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
