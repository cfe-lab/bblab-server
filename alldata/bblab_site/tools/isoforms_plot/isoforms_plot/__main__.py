from argparse import ArgumentParser
from pathlib import Path
import sys
from typing import Sequence

from isoforms_plot import plotter
from isoforms_plot import inputs


def main(argv: Sequence[str]) -> int:
    parser = ArgumentParser()
    parser.add_argument("input_csv", type=Path,
                        help="Input CSV")
    parser.add_argument("output_svg", type=Path,
                        help="Output SVG")
    args = parser.parse_args(argv)

    parsed = inputs.parse(args.input_csv)
    title = parsed["title"]

    plotter.create_isoforms_plot(inputs.TRANSCRIPTS, inputs.GROUPS, title, inputs.SPLICING_SITES, args.output_svg)
    return 0


def entry() -> None:
    sys.exit(main(sys.argv[1:]))


if __name__ == '__main__': entry()  # noqa
