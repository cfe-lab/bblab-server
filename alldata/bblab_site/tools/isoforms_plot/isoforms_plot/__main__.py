from argparse import ArgumentParser
from pathlib import Path
import sys
from typing import Optional, Sequence

from isoforms_plot import plotter, parser, compiler


def main_typed(input_csv: Path, output_svg: Path, title: Optional[str] = None) -> None:
    parsed = parser.parse(input_csv)
    compiled = compiler.compile(parsed)
    plot = plotter.plot(
        compiled['transcripts'],
        compiled['groups'],
        compiled['splicing_sites'],
        title=title,
    )
    plot.save_svg(output_svg)


def main(argv: Sequence[str]) -> int:
    argparser = ArgumentParser()
    argparser.add_argument("input_csv", type=Path, help="Input CSV")
    argparser.add_argument("output_svg", type=Path, help="Output SVG")
    argparser.add_argument("--title", type=str, help="Title of the plot", default=None)
    args = argparser.parse_args(argv)
    main_typed(args.input_csv, args.output_svg, args.title)
    return 0


def entry() -> None:
    sys.exit(main(sys.argv[1:]))


if __name__ == '__main__': entry()  # noqa
