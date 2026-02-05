from argparse import ArgumentParser
from pathlib import Path
import sys
from typing import Sequence

from isoforms_plot import plotter, parser, compiler


def main(argv: Sequence[str]) -> int:
    argparser = ArgumentParser()
    argparser.add_argument("input_csv", type=Path, help="Input CSV")
    argparser.add_argument("output_svg", type=Path, help="Output SVG")
    args = argparser.parse_args(argv)

    parsed = parser.parse(args.input_csv)
    compiled = compiler.compile(parsed)

    plotter.create_isoforms_plot(
        compiled['transcripts'],
        compiled['groups'],
        compiled['title'],
        compiled['splicing_sites'],
        args.output_svg,
    )

    return 0


def entry() -> None:
    sys.exit(main(sys.argv[1:]))


if __name__ == '__main__': entry()  # noqa
