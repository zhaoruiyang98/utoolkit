from __future__ import annotations
import argparse
import logging
import sys
from argparse import Namespace
from typing import cast
from utoolkit.cover import Cover
from utoolkit.log import LoggedError
from utoolkit.log import setup_logging
from utoolkit.subtitles import VTTConvertor


def get_parser():
    parser = argparse.ArgumentParser(
        description='toolkit for processing youtube files')
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
    cover_parser.add_argument(
        "-k", "--keep", help="keep original ratio", action="store_true")
    cover_parser.add_argument(
        "--width", help="output width", type=int, default=1146)
    cover_parser.add_argument(
        "--height", help="output height", type=int, default=717)
    cover_parser.add_argument(
        "-pad", "--padding", help="add black padding", action="store_true")

    sub_parser = subparsers.add_parser("sub", help="process subtitles")
    sub_parser.add_argument("file", help="input file path")
    sub_parser.add_argument(
        "-o", "--output", help="output file path", default="")
    sub_parser.add_argument(
        "-f", "--force", help="force overwrite", action="store_true")
    sub_parser.add_argument(
        "-t", "--duration",
        help="remove events short than x milliseconds", default=100, type=int,
    )

    return parser


class CoverNameSpace(Namespace):
    file: str
    output: str
    force: bool
    extension: str
    keep: bool
    width: int
    height: int
    padding: bool


class SubNameSpace(Namespace):
    file: str
    output: str
    force: bool
    duration: int


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.verbose == 0:
        level = logging.WARNING
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG
    setup_logging(level)

    try:
        if args.subcommand == "cover":
            args = cast(CoverNameSpace, args)
            Cover(file=args.file, output=args.output, force=args.force,
                  extension=args.extension, keep=args.keep, width=args.width,
                  height=args.height, padding=args.padding).run()
        elif args.subcommand == "sub":
            args = cast(SubNameSpace, args)
            VTTConvertor(args.file, args.output, args.force, args.duration).run()
        else:
            parser.print_help()
    except LoggedError:
        sys.exit(1)


if __name__ == "__main__":
    main()
