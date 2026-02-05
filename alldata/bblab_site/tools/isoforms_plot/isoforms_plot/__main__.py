from argparse import ArgumentParser
import sys
from typing import Sequence

from isoforms_plot import plotter
from isoforms_plot import inputs


def main(argv: Sequence[str]) -> int:
    parser = ArgumentParser()
    parser.add_argument("output_svg",
                        help="Output SVG")
    args = parser.parse_args(argv)

    plotter.create_isoforms_plot(inputs.TRANSCRIPTS, inputs.GROUPS, inputs.TITLE, args.output_svg)
    return 0


def entry() -> None:
    sys.exit(main(sys.argv[1:]))


if __name__ == '__main__': entry()
