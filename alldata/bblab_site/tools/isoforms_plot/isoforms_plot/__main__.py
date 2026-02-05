from argparse import ArgumentParser

from isoforms_plot import plotter


def main():
    parser = ArgumentParser()
    parser.add_argument("output_svg",
                        help="Output SVG")
    args = parser.parse_args()

    plotter.create_isoforms_plot(None, args.output_svg)


if __name__ == '__main__':
    main()
