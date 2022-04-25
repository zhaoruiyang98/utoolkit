from __future__ import annotations
import argparse
import logging
import sys
from argparse import Namespace
from typing import cast
from cosmotoolkit.cover import Cover
from cosmotoolkit.log import LoggedError
from cosmotoolkit.log import setup_logging
from cosmotoolkit.subtitles import VTTConvertor


def get_parser():
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
        "-o", "--output", help="output file path", default="")
    sub_parser.add_argument(
        "-f", "--force", help="force overwrite", action="store_true")

    return parser


class CoverNameSpace(Namespace):
    file: str
    output: str
    force: bool
    extension: str


class SubNameSpace(Namespace):
    file: str
    output: str
    force: bool


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
            Cover(args.file, args.output, args.force, args.extension).run()
        elif args.subcommand == "sub":
            args = cast(SubNameSpace, args)
            VTTConvertor(args.file, args.output, args.force).run()
        else:
            parser.print_help()
    except LoggedError:
        sys.exit(1)


if __name__ == "__main__":
    main()
