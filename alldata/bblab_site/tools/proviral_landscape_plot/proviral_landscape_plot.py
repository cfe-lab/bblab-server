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
                    'LargeDeletion': "#AFAFAF",
                    'Inversion': "#AFAFAF"}
HIGHLIGHT_TYPE = {'InternalInversion': 'Inversion',
                  'LargeDeletion': 'Inversion'}
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
    def __init__(self):
        self.a = START_POS
        self.b = END_POS
        self.w = END_POS + 1000
        self.h = 1
        self.color = 'black'
        self.ticks = [i for i in range(1000, 10000, 1000)]

    def draw(self, x=0, y=0, xscale=1.0):
        h = self.h
        a = self.a * xscale
        b = self.b * xscale
        x = x * xscale

        d = draw.Group(transform="translate({} {})".format(x, y))
        d.append(draw.Rectangle(a, 0, b - a, h,
                                fill=self.color, stroke=self.color))

        for tick in self.ticks:
            label = str(tick)
            tick = tick * xscale
            d.append(draw.Lines(tick, 0, tick, -20, stroke=self.color))
            d.append(Label(0, label, font_size=20, offset=-40).draw(x=tick))

        d.append(Label(0, 'Nucleotide Position', font_size=20, offset=-70).draw(x=(b-a)/2))

        return d


class LegendAndPercentages:
    def __init__(self, defect_percentages, highlighted, total_samples):
        self.a = START_POS
        self.b = END_POS
        self.w = self.b - self.a
        self.defect_types = defect_percentages.keys()
        self.highlighted_types = highlighted
        self.defect_percentages = defect_percentages
        self.num_samples = total_samples
        self.num_lines = (len(self.defect_types) + len(self.highlighted_types))/3
        self.h = 20 * self.num_lines

    def draw(self, x=0, y=0, xscale=1.0):
        h = self.h
        a = self.a * xscale
        b = self.b * xscale
        column_space = (b - a) / 3
        barlen = 300 * xscale
        barheight = 10
        x = x * xscale

        sidebar_x = b + 10
        sidebar_ystart = h + 120 + self.num_samples * 11

        d = draw.Group(transform="translate({} {})".format(x, y))

        d.append(Label(0, "Seq.", font_size=15, offset=sidebar_ystart/2+10).draw(x=(a - 30)))
        d.append(Label(0, f"N={self.num_samples}", font_size=15, offset=sidebar_ystart/2-10).draw(x=(a - 30)))

        ypos = h + 20
        for num, defect in enumerate(self.defect_types):
            try:
                color = DEFECT_TO_COLOR[defect]
            except KeyError:
                print(f"No color defined for defect {defect}")
                continue

            if num % 3 == 0:
                xpos = a
                ypos -= 20
            elif num % 3 == 1:
                xpos = a + column_space
            else:
                xpos = a + 2 * column_space

            # legend entries
            d.append(draw.Rectangle(xpos, ypos, barlen, barheight, fill=color, stroke=color))
            d.append(Label(0, defect, font_size=15, offset=ypos).draw(x=(a + xpos + barlen + 30)))

            # percentage sidebar
            sidebar_height = self.defect_percentages[defect] / 100 * 11 * self.num_samples
            sidebar_label = f'{round(self.defect_percentages[defect], 1)}%'
            fontsize = 15
            sidebar_ystart -= sidebar_height
            sidebar_label_y = fontsize / 2 + sidebar_ystart + 0.5 * sidebar_height
            d.append(draw.Rectangle(sidebar_x, sidebar_ystart, 10, sidebar_height, fill=color, stroke=color))
            d.append(draw.Text(text=sidebar_label,
                               fontSize=fontsize,
                               x=sidebar_x+40,
                               y=sidebar_label_y,
                               font_family='monospace',
                               center=True,
                               fill=color))

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
        self.figure.add(Multitrack(self.curr_multitrack), gap=1)
        self.curr_multitrack = []

    def add_xaxis(self):
        self.figure.add(XAxis(), padding=20, gap=100)

    def legends_and_percentages(self, defect_percentages, highlight_types, total_samples):
        self.figure.add(LegendAndPercentages(defect_percentages, highlight_types, total_samples))


def sort_csv_lines(lines):
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
        yield all_rows_this_defect


def create_proviral_plot(input_file, output_svg):
    defect_percentages = {}
    highlighted_set = set()
    figure = Figure()
    plot = ProviralLandscapePlot(figure)
    lines = list(DictReader(input_file))
    for all_rows_this_defect in sort_csv_lines(lines):
        defect = all_rows_this_defect[0]['defect']
        for row in all_rows_this_defect:
            if int(row['ref_start']) < int(row['ref_end']):
                xstart = int(row['ref_start'])
                xend = int(row['ref_end'])
                is_highlighted = row['highlighted']
            else:
                xstart = int(row['ref_end'])
                xend = int(row['ref_start'])
                is_highlighted = True
            plot.add_line(row['samp_name'],
                          xstart,
                          xend,
                          defect,
                          is_highlighted)
            if is_highlighted:
                try:
                    highlighted_type = HIGHLIGHT_TYPE[defect]
                    highlighted_set.add(highlighted_type)
                except KeyError:
                    print(f"No highlight type defined for {defect}")
                    pass
        num_samples = len(set([row['samp_name'] for row in all_rows_this_defect]))
        defect_percentages[defect] = num_samples

    total_samples = len(set([row['samp_name'] for row in lines if row['defect'] in DEFECT_TO_COLOR.keys()]))
    for defect, number in defect_percentages.items():
        if defect not in DEFECT_TO_COLOR.keys():
            continue
        percentage = number / total_samples * 100
        defect_percentages[defect] = percentage

    # draw the final line in the plot
    plot.draw_current_multitrack()
    plot.add_xaxis()
    plot.legends_and_percentages(defect_percentages, highlighted_set, total_samples)
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
