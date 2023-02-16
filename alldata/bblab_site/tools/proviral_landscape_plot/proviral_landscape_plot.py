from csv import DictReader
from argparse import ArgumentParser
from genetracks import Figure, Track, Multitrack

DEFECT_TO_COLOR = {'5DEFECT': "#440154",
                   'Hypermut': "#1fa187",
                   'Intact': "#a0da39",
                   'Inferred_Intact': "#a0da39",
                   'InternalInversion': "#7f0584",
                   'LargeDeletion': "#365c8d"}
HIGHLIGHT_COLORS = {'InternalInversion': "#AFAFAF",
                    'LargeDeletion': "#AFAFAF"}
START_POS = 638
END_POS = 9632


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
        self.figure.add(Multitrack(self.curr_multitrack))
        self.curr_multitrack = []


def create_proviral_plot(input_file, output_svg):
    reader = DictReader(input_file)
    figure = Figure()
    plot = ProviralLandscapePlot(figure)
    for row in reader:
        plot.add_line(row['samp_name'],
                      int(row['ref_start']),
                      int(row['ref_end']),
                      row['defect'],
                      row['highlighted'])
    # draw the final line in the plot
    plot.draw_current_multitrack()
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
