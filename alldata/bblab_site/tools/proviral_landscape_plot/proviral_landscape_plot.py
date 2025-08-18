from csv import DictReader
from argparse import ArgumentParser
from genetracks import Figure, Track, Multitrack, Label
from itertools import groupby
from operator import itemgetter
import drawsvg as draw
from collections import defaultdict
from math import ceil

DEFECT_TO_COLOR = {"5' Defect": "#44AA99",
                   'Hypermutated': "#88CCEE",
                   'Intact': "#332288",
                   'Inversion': "#999933",
                   'Large Deletion': "#117733",
                   'Premature Stop': "#CC6677",
                   'Chimera': "#AA4499",
                   'Scrambled': "#882255",
                   'Large Insertion': "#DDCC77",
                   'Frameshift': "#DDAA77",
                   'Divergence': "#661100",
                   }

# colors are chosen from Paul Tol's muted color scheme, which is color-blind safe
# if another defect color is needed, this one is recommended: #DDCC77
HIGHLIGHT_COLORS = {'Defect Region': "black",
                    'Inverted Region': "#AFAFAF",
                    }

DEFECT_TYPE = {'LargeDeletion': 'Large Deletion',
               'LongDeletion': 'Large Deletion',
               'InternalInversion': 'Inversion',
               'ScramblePlus': 'Scrambled',
               'ScrambleMinus': 'Scrambled',
               'ScrambleCheck': 'Scrambled',
               'Scramble': 'Scrambled',
               'Hypermut': 'Hypermutated',
               'APOBECHypermutation': 'Hypermutated',
               'Intact': 'Intact',
               'Inferred_Intact': 'Intact',
               'PrematureStop_OR_AAtooLong_OR_AAtooShort': 'Premature Stop',
               'PrematureStop_OR_AAtooLong_OR_AAtooShort_GagNoATG': 'Premature Stop',
               'Inferred_PrematureStopORInframeDEL': 'Premature Stop',
               'Inferred_PrematureStopORInframeDEL_GagNoATGandFailed': 'Premature Stop',
               'Inferred_PrematureStopORInframeDEL_GagNoATG': 'Premature Stop',
               'InternalStop': "Premature Stop",
               'MutatedStopCodon': "Premature Stop",
               'MutatedStartCodon': "Premature Stop",
               'SequenceDivergence': "Divergence",
               'Deletion': "Premature Stop",
               'Insertion': "Large Insertion",
               'Frameshift': "Frameshift",
               '5DEFECT': "5' Defect",
               '5DFECT_IntoGag': "5' Defect",  # this is a typo in HIVSeqinR
               '5DEFECT_GagNoATGGagPassed': "5' Defect",
               '5DEFECT_GagNoATGGagFailed': "5' Defect",
               'Inferred_Intact_GagNoATG': "5' Defect",
               'Inferred_Intact_NoGag': "5' Defect",
               'Intact_GagNoATG': "5' Defect",
               'MajorSpliceDonorSiteMutated': "5' Defect",
               'PackagingSignalDeletion': "5' Defect",
               'PackagingSignalNotComplete': "5' Defect",
               'RevResponseElementDeletion': "5' Defect",
               'NonHIV': 'Chimera',
               'AlignmentFailed': 'Chimera',
               'UnknownNucleotide': 'Chimera',
               }

# There are some defects where we don't care about the alignment and just want to plot lines:
LINE_DEFECTS = ['Hypermutated', 'Intact', 'Premature Stop']
DEFECT_ORDER = {'Intact': 10,
                'Hypermutated': 20,
                "5' Defect": 30,
                'Large Deletion': 40,
                'Inversion': 50,
                'Premature Stop': 60,
                'Large Insertion': 63,
                'Frameshift': 67,
                'Scrambled': 70,
                'Chimera': 80,
                }

START_POS = 638
END_POS = 9632
LEFT_PRIMER_END = 666
RIGHT_PRIMER_START = 9604
GAG_END = 2292
XOFFSET = 400
SMALLEST_GAP = 50


def defect_order(defect):
    defect_type = DEFECT_TYPE[defect]
    try:
        order = DEFECT_ORDER[defect_type]
    except KeyError:
        max_order = max(DEFECT_ORDER.values())
        order = max_order + 1
        DEFECT_ORDER[defect] = order
        print(f"The order of defect type {defect_type} was not specified -"
              f" it will just get appended to the end of the plot.")
    return order


class XAxis:
    def __init__(self, h=3):
        self.a = START_POS + XOFFSET
        self.b = END_POS + XOFFSET
        self.w = END_POS + XOFFSET + 1500
        self.h = h
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
            x_tick = (tick + XOFFSET) * xscale
            d.append(draw.Lines(x_tick, 0, x_tick, -20, stroke=self.color, stroke_width=h))
            d.append(Label(0, label, font_size=20, offset=-40).draw(x=x_tick))

        d.append(Label(0, 'Nucleotide Position', font_size=20, offset=-70).draw(x=a + (b - a) / 2))

        return d


class LegendAndPercentages:
    def __init__(self, defect_percentages, highlighted, total_samples, lineheight, xaxisheight):
        self.a = START_POS + XOFFSET
        self.b = END_POS + XOFFSET
        self.w = self.b - self.a
        self.defect_types = defect_percentages.keys()
        self.highlighted_types = highlighted
        self.defect_percentages = defect_percentages
        self.num_samples = total_samples
        self.num_lines = (len(self.defect_types) + len(self.highlighted_types)) / 3
        self.h = 20 * self.num_lines
        self.lineheight = lineheight
        self.xaxisheight = xaxisheight

    def add_legend(self, a, column_space, barlen, barheight, drawing):
        ypos_first = self.h
        num_defects = 0
        num_defects_per_column = ceil((len(self.defect_types) + len(self.highlighted_types)) / 3)
        all_entries = [defect for defect in self.defect_types] + [highlight for highlight in self.highlighted_types]
        for defect in all_entries:
            try:
                color = DEFECT_TO_COLOR[defect]
            except KeyError:
                try:
                    color = HIGHLIGHT_COLORS[defect]
                except KeyError:
                    print(f"No color defined for defect {defect}")
                    continue

            if num_defects < num_defects_per_column:
                xpos = a
            elif num_defects < 2 * num_defects_per_column:
                xpos = a + column_space
            else:
                xpos = a + 2 * column_space
            if num_defects % num_defects_per_column == 0:
                ypos = ypos_first
            else:
                ypos -= 20
            num_defects += 1

            # legend entries
            drawing.append(draw.Rectangle(xpos, ypos, barlen, barheight, fill=color, stroke=color))
            drawing.append(Label(0, defect, font_size=15, offset=ypos).draw(x=(a + xpos + barlen)))

    def add_sidebar(self, sidebar_x, sidebar_ystart, fontsize, drawing):
        pending_percentages = []
        for defect in self.defect_types:
            try:
                color = DEFECT_TO_COLOR[defect]
            except KeyError:
                print(f"No color defined for defect {defect}")
                continue

            # percentage sidebar
            sidebar_height = self.defect_percentages[defect] / 100 * (self.lineheight + 1) * self.num_samples
            sidebar_label = f'{round(self.defect_percentages[defect], 1)}%'
            sidebar_ystart -= sidebar_height
            sidebar_label_y = fontsize / 4 + sidebar_ystart + 0.5 * sidebar_height
            if self.defect_percentages[defect] < 0.1:
                # skip very small percentages
                pending_percentages.append((self.defect_percentages[defect], sidebar_height, color))
            else:
                drawing.append(draw.Rectangle(sidebar_x, sidebar_ystart, 10, sidebar_height, fill=color, stroke=color))
                drawing.append(draw.Text(text=sidebar_label,
                                         font_size=fontsize,
                                         x=sidebar_x + 60,
                                         y=sidebar_label_y - 10,
                                         font_family='monospace',
                                         center=True,
                                         fill=color))
                if pending_percentages:
                    pending_ystart = sidebar_ystart + sidebar_height
                    self.draw_pending_percentages(drawing, pending_percentages, fontsize, sidebar_x, pending_ystart)
                    pending_percentages = []
        if pending_percentages:
            self.draw_pending_percentages(drawing, pending_percentages, fontsize, sidebar_x, sidebar_ystart)

    @staticmethod
    def draw_pending_percentages(drawing, pending_percentages, fontsize, sidebar_x, sidebar_ystart):
        total_pending = sum(elem[0] for elem in pending_percentages)
        pending_height = sum(elem[1] for elem in pending_percentages)
        pending_label = f'{round(total_pending, 1)}%'
        pending_label_y = fontsize / 4 + sidebar_ystart + 0.5 * pending_height
        if len(pending_percentages) > 1:
            color = 'black'
        else:
            # if it's just one pending defect, keep the regular color and leave out the black bar
            color = pending_percentages[0][2]
        drawing.append(
            draw.Rectangle(sidebar_x, sidebar_ystart, 10, pending_height, fill=color, stroke=color))
        drawing.append(draw.Text(text=pending_label,
                                 font_size=fontsize,
                                 x=sidebar_x + 60,
                                 y=pending_label_y,
                                 font_family='monospace',
                                 center=True,
                                 fill=color))

    def draw(self, x=0, y=0, xscale=1.0):
        h = self.h
        a = self.a * xscale
        b = self.b * xscale
        column_space = (b - a) / 3
        barlen = 300 * xscale
        barheight = 10
        x = x * xscale
        sidebar_x = b + 10
        sidebar_ystart = h + self.xaxisheight + self.num_samples * (self.lineheight + 1)
        yaxis_label_height = h + self.xaxisheight + self.num_samples * (self.lineheight + 1) / 2
        fontsize = 20

        d = draw.Group(transform="translate({} {})".format(x, y))

        d.append(Label(-10, "Seq.", font_size=20, offset=yaxis_label_height + 12).draw(x=(a - 30)))
        d.append(Label(-10, f"N={self.num_samples}", font_size=20, offset=yaxis_label_height - 12).draw(x=(a - 30)))

        self.add_legend(a, column_space, barlen, barheight, d)
        self.add_sidebar(sidebar_x, sidebar_ystart, fontsize, d)

        return d


class ProviralLandscapePlot:
    def __init__(self, figure, tot_samples):
        self.curr_samp_name = ''
        self.defects = set()
        self.figure = figure
        self.curr_multitrack = []
        self.tot_samples = tot_samples
        self.lineheight = 500 / self.tot_samples if self.tot_samples > 0 else 0
        if self.lineheight > 5:
            self.lineheight = 5
        self.xaxisheight = 0

    def add_line(self, samp_name, xstart, xend, defect_type, highlight):
        highlight = None

        is_first = False
        if defect_type not in DEFECT_TO_COLOR.keys():
            print(f"Unknown defect: {defect_type}")
            return
        if samp_name != self.curr_samp_name:
            if self.curr_samp_name != '':
                self.draw_current_multitrack()
            self.curr_samp_name = samp_name
            is_first = True
        if defect_type in LINE_DEFECTS and highlight != 'Defect Region':
            # draw the entire line once and skip all others, unless they're highlighted as the defect region
            if is_first:
                xstart = LEFT_PRIMER_END
                xend = RIGHT_PRIMER_START
                highlight = False
            else:
                return
        if is_first:
            # add the primers to start and end
            left_primer = self.make_gene_track(START_POS, LEFT_PRIMER_END, defect_type)
            self.curr_multitrack.append(left_primer)
            right_primer = self.make_gene_track(RIGHT_PRIMER_START, END_POS, defect_type)
            self.curr_multitrack.append(right_primer)
        if defect_type == "5' Defect":
            if is_first:
                # draw everything after the end of gag as a line
                after_gag = self.make_gene_track(GAG_END, RIGHT_PRIMER_START, defect_type)
                self.curr_multitrack.append(after_gag)
            if xstart > GAG_END:
                return
            elif xend > GAG_END:
                xend = GAG_END
        self.defects.add(defect_type)
        curr_track = self.make_gene_track(xstart, xend, defect_type, highlight=highlight)
        self.curr_multitrack.append(curr_track)

    def make_gene_track(self, xstart, xend, defect_type, highlight=False):
        color = DEFECT_TO_COLOR[defect_type]
        if highlight:
            try:
                color = HIGHLIGHT_COLORS[highlight]
            except KeyError:
                print(f"No highlighted color defined for {defect_type} defect. Will use regular color.")
                pass
        if xstart < START_POS:
            xstart = START_POS
        if xend > END_POS:
            xend = END_POS
        track = Track(xstart + XOFFSET, xend + XOFFSET, color=color, h=self.lineheight)
        return track

    def draw_current_multitrack(self):
        # draw line and reset multitrack
        if self.curr_multitrack:
            self.figure.add(Multitrack(self.curr_multitrack), gap=1)
        self.curr_multitrack = []

    def add_xaxis(self):
        padding = 20
        gap = 100
        xaxis_thickness = 3
        self.figure.add(XAxis(h=xaxis_thickness), padding=padding, gap=gap)
        self.xaxisheight = padding + gap + xaxis_thickness

    def legends_and_percentages(self, defect_percentages, highlight_types):
        self.figure.add(LegendAndPercentages(defect_percentages,
                                             highlight_types,
                                             self.tot_samples,
                                             self.lineheight,
                                             self.xaxisheight))


def sort_csv_lines(lines):
    lines.sort(key=lambda elem: defect_order(elem['defect'].strip()))
    for _, defect_rows in groupby(lines, key=lambda elem: DEFECT_TYPE[elem['defect']]):
        defect_rows = list(defect_rows)
        defect_rows.sort(key=lambda elem: elem['samp_name'].strip())
        all_rows_by_sample = []
        for _, samp_rows in groupby(defect_rows, itemgetter('samp_name')):
            samp_rows = list(samp_rows)
            samp_rows.sort(key=lambda elem: int(elem['ref_start'].strip()))
            if DEFECT_TYPE[samp_rows[0]['defect']] not in ["5' Defect"] + LINE_DEFECTS:
                # We want to remove 50bp gaps, unless it's a 5'defect. Can also skip line defects
                for i, row in enumerate(samp_rows):
                    ref_start = int(row['ref_start'].strip())
                    ref_end = int(row['ref_end'].strip())
                    if row['is_inverted'] or row['is_defective']:
                        continue
                    if i == 0:
                        if (ref_start - LEFT_PRIMER_END) < SMALLEST_GAP and ref_end > LEFT_PRIMER_END:
                            row['ref_start'] = str(LEFT_PRIMER_END)
                        continue
                    prev_ref_end = int(samp_rows[i - 1]['ref_end'].strip())
                    if (ref_start - prev_ref_end) < SMALLEST_GAP and ref_start > prev_ref_end:
                        row['ref_start'] = samp_rows[i-1]['ref_end']
                        samp_rows[i - 1]['ref_end'] = row['ref_end']  # this is for sorting purposes
                prev_ref_start = int(samp_rows[-1]['ref_start'].strip())
                prev_ref_end = int(samp_rows[-1]['ref_end'].strip())
                if (RIGHT_PRIMER_START - prev_ref_end) < SMALLEST_GAP and prev_ref_start < RIGHT_PRIMER_START:
                    samp_rows[-1]['ref_end'] = str(RIGHT_PRIMER_START)
            all_rows_by_sample.append(samp_rows)
        all_rows_by_sample.sort(key=sort_defect_rows)
        all_rows_this_defect = [item for sublist in all_rows_by_sample for item in sublist]
        yield all_rows_this_defect


def sort_defect_rows(samp_list):
    first_ref_start = int(samp_list[0]['ref_start'].strip())
    first_ref_end = int(samp_list[0]['ref_end'].strip())
    if first_ref_start <= LEFT_PRIMER_END:
        return -first_ref_end
    else:
        return -LEFT_PRIMER_END


def order_samples_by_gaps(rows, threshold=SMALLEST_GAP):
    """
    Within a defect category, sort samples by their gaps:
    1. Identify and record each gap as (start, end, size).
    2. For each sample, sort its gaps by descending size.
    3. Build per-sample lists of (start, end) from those sorted gaps.
    4. Pad shorter lists with (END_POS+1, END_POS+1) to equal length.
    5. Sort samples lexicographically by these flattened (start,end) lists,
       ties on equal starts are broken by earlier ends.
    """
    # group rows by sample
    sample_rows = defaultdict(list)
    for r in rows:
        sample_rows[r['samp_name'].strip()].append(r)
    # compute gaps per sample
    sample_gap_feats = {}
    max_len = 0
    for samp, segs in sample_rows.items():
        segs_sorted = sorted(segs, key=lambda x: int(x['ref_start'].strip()))
        prev_end = START_POS
        feats = []  # list of (start,end,size)
        for seg in segs_sorted:
            start = int(seg['ref_start'].strip())
            if start - prev_end > threshold:
                size = start - prev_end
                feats.append((prev_end, start, size))
            prev_end = max(prev_end, int(seg['ref_end'].strip()))
        if END_POS - prev_end > threshold:
            size = END_POS - prev_end
            feats.append((prev_end, END_POS, size))
        # sort features by descending size
        feats_sorted = sorted(feats, key=lambda x: x[2], reverse=True)
        # extract only (start,end)
        pos_list = [(s, e) for s, e, _ in feats_sorted]
        sample_gap_feats[samp] = pos_list
        max_len = max(max_len, len(pos_list))
    # pad with out-of-range pairs to equal length
    pad_pair = (END_POS + 1, END_POS + 1)
    for samp, pos_list in sample_gap_feats.items():
        if len(pos_list) < max_len:
            pos_list.extend([pad_pair] * (max_len - len(pos_list)))
        sample_gap_feats[samp] = pos_list
    # final sort: flatten each (start,end) list and compare lex
    def sample_key(samp):
        flat = []
        for start, end in sample_gap_feats[samp]:
            flat.append(start)
            flat.append(end)
        return tuple(flat)
    sorted_samples = sorted(sample_gap_feats.keys(), key=sample_key)
    return sorted_samples


def create_proviral_plot(input_file, output_svg):
    # read all rows, set up figure and counters
    lines = list(DictReader(input_file))
    # total unique samples (across all defects)
    total_samples = len(set(r['samp_name'].strip() for r in lines if r['defect'].strip() in DEFECT_TYPE))
    figure = Figure()
    plot = ProviralLandscapePlot(figure, total_samples)
    defect_percentages = defaultdict(int)
    highlighted_set = set()
    # group and plot by defect category, preserving category order
    for all_rows_this_defect in sort_csv_lines(lines):
        defect = DEFECT_TYPE[all_rows_this_defect[0]['defect'].strip()]
        # within this defect, sort samples by their gap patterns
        # collect rows for this defect
        rows = all_rows_this_defect
        sample_rows = defaultdict(list)
        for r in rows:
            sample_rows[r['samp_name'].strip()].append(r)
        # determine order of samples in this defect
        sample_order = order_samples_by_gaps(rows)
        # plot each sample in the defect group
        for samp in sample_order:
            segs = sample_rows[samp]
            segs.sort(key=lambda x: int(x['ref_start'].strip()))
            for row in segs:
                xstart = int(row['ref_start'].strip())
                xend = int(row['ref_end'].strip())
                highlighted = False
                if row['is_defective'].strip():
                    # TODO: incorporate this when we get ranges info from proviral.
                    # highlighted_set.add('Defect Region')
                    highlighted = 'Defect Region'
                elif row['is_inverted'].strip():
                    highlighted_set.add('Inverted Region')
                    highlighted = 'Inverted Region'
                plot.add_line(samp, xstart, xend, defect, highlighted)
        # count samples in this defect for percentages
        defect_percentages[defect] += len(sample_order)

    # convert counts to percentages
    for defect, number in defect_percentages.items():
        if defect not in DEFECT_TO_COLOR:
            continue
        defect_percentages[defect] = number / total_samples * 100
    # finalize plot
    plot.draw_current_multitrack()
    plot.add_xaxis()
    plot.legends_and_percentages(defect_percentages, highlighted_set)
    figure.show(w=900).save_svg(output_svg)


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
