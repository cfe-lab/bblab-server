from argparse import ArgumentParser
from pathlib import Path
import sys
from typing import Sequence

from isoforms_plot import lexer, plotter, parser, compiler


def main_typed(input_csv: Path, output_svg: Path) -> None:
    lexed = lexer.lex(input_csv)
    parsed = parser.parse(lexed)
    compiled = compiler.compile(parsed)
    plot = plotter.plot(
        compiled.transcripts,
        compiled.groups,
        compiled.splicing_sites,
        compiled.title,
    )
    plot.save_svg(output_svg)


def main(argv: Sequence[str]) -> int:
    argparser = ArgumentParser()
    argparser.add_argument("input_csv", type=Path, help="Input CSV")
    argparser.add_argument("output_svg", type=Path, help="Output SVG")
    args = argparser.parse_args(argv)
    main_typed(args.input_csv, args.output_svg)
    return 0


def entry() -> None:
    sys.exit(main(sys.argv[1:]))


if __name__ == '__main__': entry()  # noqa
