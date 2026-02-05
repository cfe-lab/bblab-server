from argparse import ArgumentParser
from pathlib import Path
import sys
from typing import Sequence

from isoforms_plot import plotter
from isoforms_plot import parser


def main(argv: Sequence[str]) -> int:
    argparser = ArgumentParser()
    argparser.add_argument("input_csv", type=Path, help="Input CSV")
    argparser.add_argument("output_svg", type=Path, help="Output SVG")
    args = argparser.parse_args(argv)

    parsed = parser.parse(args.input_csv)
    title = parsed["title"]

    plotter.create_isoforms_plot(parser.TRANSCRIPTS, parser.GROUPS, title, parser.SPLICING_SITES, args.output_svg)
    return 0


def entry() -> None:
    sys.exit(main(sys.argv[1:]))


if __name__ == '__main__': entry()  # noqa
