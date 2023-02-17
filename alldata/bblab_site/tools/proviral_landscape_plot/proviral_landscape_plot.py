from csv import DictReader
from argparse import ArgumentParser
from genetracks import Figure, Track, Multitrack, Label
from itertools import groupby
from operator import itemgetter
import drawSvg as draw

DEFECT_TO_COLOR = {'5DEFECT': "#440154",
                   'Hypermut': "#1fa187",
                   'Intact': "#a0da39",
                   'Inferred_Intact': "#a0da39",
                   'InternalInversion': "#7f0584",
                   'LargeDeletion': "#365c8d"}
HIGHLIGHT_COLORS = {'InternalInversion': "#AFAFAF",
                    'LargeDeletion': "#AFAFAF"}
DEFECT_ORDER = {'Intact': 10,
                'Inferred_Intact': 20,
                'Hypermut': 30,
                '5DEFECT': 40,
                'LargeDeletion': 50,
                'InternalInversion': 60}
START_POS = 638
END_POS = 9632


def defect_order(defect):
    try:
        order = DEFECT_ORDER[defect]
    except KeyError:
        max_order = max(DEFECT_ORDER.values())
        order = max_order + 1
        DEFECT_ORDER[defect] = order
        print(f"The order of defect {defect} was not specified - it will just get appended to the end of the plot.")
    return order


def make_gene_track(xstart, xend, defect_type, is_highlighted):
    color = DEFECT_TO_COLOR[defect_type]
    if is_highlighted:
        try:
            color = HIGHLIGHT_COLORS[defect_type]
        except KeyError:
            print(f"No highlighted color defined for {defect_type} defect. Will use regular color.")
            pass
    if xstart < START_POS:
        xstart = START_POS
    if xend > END_POS:
        xend = END_POS
    track = Track(xstart, xend, color=color)
    return track


class XAxis:
    def __init__(self, width=END_POS):
        self.a = START_POS
        self.b = END_POS
        self.w = width
        self.h = 1
        self.color = 'black'
        self.ticks = [i for i in range(1000, 10000, 1000)]

    def draw(self, x=0, y=0, xscale=1.0):
        h = self.h
        a = self.a * xscale
        b = self.b * xscale
        x = x * xscale

        # assert isinstance(x, float) and isinstance(y, float)
        d = draw.Group(transform="translate({} {})".format(x, y))
        d.append(draw.Rectangle(a, 0, b - a, h,
                                fill=self.color, stroke=self.color))

        for tick in self.ticks:
            label = str(tick)
            tick = tick * xscale
            d.append(draw.Lines(tick, 0, tick, -20, stroke=self.color))
            d.append(Label(0, label, font_size=20, offset=-40).draw(x=tick))

        d.append(Label(0, 'Nucleotide Position', font_size=20, offset=-60).draw(x=(b-a)/2))

        return d


class ProviralLandscapePlot:
    def __init__(self, figure):
        self.curr_samp_name = ''
        self.defects = set()
        self.figure = figure
        self.curr_multitrack = []

    def add_line(self, samp_name, xstart, xend, defect_type, is_highlighted):
        if defect_type not in DEFECT_TO_COLOR.keys():
            # we can skip non HIV?
            if defect_type != 'NonHIV':
                print(f"Unknown defect: {defect_type}")
            return
        if samp_name != self.curr_samp_name:
            if self.curr_samp_name != '':
                self.draw_current_multitrack()
            self.curr_samp_name = samp_name
        self.defects.add(defect_type)
        curr_track = make_gene_track(xstart, xend, defect_type, is_highlighted)
        self.curr_multitrack.append(curr_track)

    def draw_current_multitrack(self):
        # draw line and reset multitrack
        self.figure.add(Multitrack(self.curr_multitrack), gap=0)
        self.curr_multitrack = []

    def add_xaxis(self):
        self.figure.add(XAxis(), padding=20, gap=80)


def create_proviral_plot(input_file, output_svg):
    figure = Figure()
    plot = ProviralLandscapePlot(figure)
    lines = list(DictReader(input_file))
    lines.sort(key=lambda elem: defect_order(elem['defect']))
    for _, defect_rows in groupby(lines, itemgetter('defect')):
        defect_rows = list(defect_rows)
        defect_rows.sort(key=lambda elem: elem['samp_name'])
        all_rows_by_sample = []
        for _, samp_rows in groupby(defect_rows, itemgetter('samp_name')):
            samp_rows = list(samp_rows)
            samp_rows.sort(key=lambda elem: int(elem['ref_start']))
            all_rows_by_sample.append(samp_rows)
        all_rows_by_sample.sort(key=lambda samp_list: -int(samp_list[0]['ref_end']))
        all_rows_this_defect = [item for sublist in all_rows_by_sample for item in sublist]
        for row in all_rows_this_defect:
            ref_start = int(row['ref_start'])
            ref_end = int(row['ref_end'])
            if ref_start > ref_end:
                plot.add_line(row['samp_name'],
                              ref_end,
                              ref_start,
                              row['defect'],
                              is_highlighted=True)
            else:
                plot.add_line(row['samp_name'],
                              ref_start,
                              ref_end,
                              row['defect'],
                              row['highlighted'])
    # draw the final line in the plot
    plot.draw_current_multitrack()
    plot.add_xaxis()
    figure.show(w=900).saveSvg(output_svg)


def main():
    parser = ArgumentParser()
    parser.add_argument("proviral_landscape_csv",
                        help="Proviral landscape input file, produced by proviral pipeline")
    parser.add_argument("output_svg",
                        help="Output SVG")
    args = parser.parse_args()

    with open(args.proviral_landscape_csv, 'r') as input_file:
        create_proviral_plot(input_file, args.output_svg)


if __name__ == '__main__':
    main()
