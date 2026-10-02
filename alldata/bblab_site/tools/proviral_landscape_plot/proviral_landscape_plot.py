import os
import re
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

# the columns an input csv has to provide
REQUIRED_COLUMNS = ['samp_name', 'ref_start', 'ref_end', 'defect',
                    'is_defective', 'is_inverted']

START_POS = 638
END_POS = 9632
LEFT_PRIMER_END = 666
RIGHT_PRIMER_START = 9604
GAG_END = 2292
XOFFSET = 400
SMALLEST_GAP = 50

# height (in unscaled plot units) that is reserved for the sample tracks of a
# single plot. When several plots are drawn on one page every plot gets the
# same amount of room for its samples, so that the proportions of the defect
# categories are directly comparable between plots. A page works out its own
# height from the size of the paper, this is only the fallback.
SAMPLE_BLOCK_HEIGHT = 800
# tracks are never squeezed below this height; plots with a huge number of
# samples make every plot on the page taller instead
MIN_LINEHEIGHT = 0.5
# vertical space inserted between two consecutive sample tracks
SAMPLE_GAP = 1

# the leading participant number of a sample name, e.g. the 0380 of
# 0380X00415ANFL11M11-NFLHIVDNA_S158
PARTICIPANT_PATTERN = re.compile(r'^(\d{4})(?!\d)')

# grid layout. A page that is tied to a paper size works in millimetres; the
# plots themselves are drawn in "plot units" (PLOT_WIDTH units wide) and scaled
# onto the page.
GRID_COLUMNS = 3
PLOT_WIDTH = 900
PLOT_GAP_MM = 4.0
PAGE_MARGIN_MM = 8.0
# the same two, in plot units, for a page that is not tied to a paper size
PLOT_GAP = 40
PAGE_MARGIN = 20

# named paper sizes in millimetres, as (width, height). A page is laid out in
# plot units and then given the proportions of the paper, so the drawing is
# resolution independent: the svg declares its physical size and prints, or
# rasterizes, at whatever resolution is asked for.
PAGE_SIZES_MM = {
    'a4-landscape': (297.0, 210.0),
    'a4-portrait': (210.0, 297.0),
}
DEFAULT_PAGE_SIZE = 'a4-landscape'

# A page is laid out in millimetres of paper and the plots are drawn in plot
# units, scaled onto it. Text is therefore specified by how tall it should end
# up on the page, and converted to plot units once the scale is known.
TITLE_FONT_MM = 3.4
SUBTITLE_FONT_MM = 2.4
XAXIS_FONT_MM = 2.4
SIDEBAR_FONT_MM = 2.4
LEGEND_FONT_MM = 2.6

# vertical space each plot needs on the page for everything that is not a
# sample track. Both are worked out from the factors the drawing itself uses
# (see PlotTitle and ProviralLandscapePlot.add_xaxis), so the height budget
# cannot drift away from what is really drawn.
# the title is two lines of text, the gap under it is in plot units and added
# by the page, which knows how big a plot unit is on the paper
TITLE_GAP_UNITS = 10
TITLE_CHROME_MM = 1.6 * TITLE_FONT_MM + 1.6 * SUBTITLE_FONT_MM
# the x axis is a thin line with room above it for the gap to the tracks and
# room below it for the tick labels and the axis title
AXIS_PADDING_FACTOR = 0.5
AXIS_GAP_FACTOR = 2.5
AXIS_THICKNESS_FACTOR = 0.15
# the space the tick labels and the axis title need below the axis line, as a
# multiple of the axis font size; XAxis reserves exactly this much
AXIS_LABEL_SPACE_FACTOR = 4.0
# How far a plot hangs below the box the page lays it out in. The axis title
# sits further below the axis line than the figure reserves for the axis, so
# the drawn axis reaches past the bottom of that box by this much, as a
# multiple of the axis font size.
AXIS_TITLE_OFFSET_FACTOR = 3.5
AXIS_OVERHANG_FACTOR = AXIS_TITLE_OFFSET_FACTOR + 0.2 - AXIS_GAP_FACTOR
XAXIS_CHROME_MM = (AXIS_PADDING_FACTOR + AXIS_GAP_FACTOR
                   + AXIS_THICKNESS_FACTOR + AXIS_LABEL_SPACE_FACTOR) \
    * XAXIS_FONT_MM
# the shared legend strip below the grid: one row of entries plus padding
LEGEND_ROW_MM = 3.5
LEGEND_PADDING_MM = 3.0
# the gap a turned legend keeps from the plots around it when it goes into a
# free corner of the grid instead of into the strip below it
LEGEND_CORNER_GAP_MM = 3.0

# Plot-unit font sizes for a page that is not tied to a paper size. These only
# matter for --page-size fit.
TITLE_FONT_SIZE = 34
SUBTITLE_FONT_SIZE = 21
XAXIS_FONT_SIZE = 20
SIDEBAR_FONT_SIZE = 20

# default HXB2 landmarks for the small overview graphic
# assigned to three frames (0/1/2) so overlapping genes stack vertically
# tat and rev have multiple exons, so we include both parts
LANDMARKS = [
    {"name": "5'LTR", 'start': 1, 'end': 634, 'colour': '#e0e0e0', 'frame': 0},
    {'name': 'gag', 'start': 790, 'end': GAG_END, 'colour': '#a6cee3', 'frame': 0},
    {'name': 'pol', 'start': 2085, 'end': 5096, 'colour': '#1f78b4', 'frame': 2},
    {'name': 'vif', 'start': 5041, 'end': 5619, 'colour': '#fb9a99', 'frame': 0},
    {'name': 'vpr', 'start': 5559, 'end': 5850, 'colour': '#fdbf6f', 'frame': 2},
    {'name': 'tat', 'start': 5831, 'end': 6045, 'colour': '#b2df8a', 'frame': 1, 'exon': 1},
    {'name': 'tat', 'start': 8379, 'end': 8469, 'colour': '#b2df8a', 'frame': 0, 'exon': 2},
    {'name': 'rev', 'start': 5970, 'end': 6045, 'colour': '#c2a5cf', 'frame': 2, 'exon': 1},
    {'name': 'rev', 'start': 8379, 'end': 8653, 'colour': '#c2a5cf', 'frame': 1, 'exon': 2},
    {'name': 'vpu', 'start': 6062, 'end': 6310, 'colour': '#ffff99', 'frame': 1},
    {'name': 'env', 'start': 6225, 'end': 8795, 'colour': '#8dd3c7', 'frame': 2},
    {'name': 'nef', 'start': 8797, 'end': 9417, 'colour': '#bebada', 'frame': 0},
    {"name": "3'LTR", 'start': 9086, 'end': 9719, 'colour': '#e0e0e0', 'frame': 1}
]

def is_truthy(value):
    """
    Check if a value should be interpreted as True.
    Accepts: '1', 'true', 't', 'yes', 'y' (case-insensitive)
    Rejects: '0', 'false', 'f', 'no', 'n', '' (empty string), and any other value
    """
    if not value:
        return False
    return value.strip().lower() in ('1', 'true', 't', 'yes', 'y')

def add_genome_overview(figure, landmarks, height=12, xoffset=XOFFSET):
    """
    Draw a simple overview of the reference (HXB2) using the provided
    landmarks list. Each landmark should be a dict with 'start', 'end', 'name'
    and optionally 'colour' and 'frame'. Coordinates are assumed to be in the
    same reference coordinate system as START_POS/END_POS; this function adds
    XOFFSET so the overview lines up with the main plot.
    """

    # Fill out missing ends (simple behaviour: end is start-1 of next)
    prev_landmark = None
    landmarks_sorted = sorted(landmarks, key=itemgetter('start'))
    for landmark in landmarks_sorted:
        landmark.setdefault('frame', 0)
        if prev_landmark and 'end' not in prev_landmark:
            prev_landmark['end'] = landmark['start'] - 1
        prev_landmark = landmark

    # Build a list of items and per-gene exon lists
    items = []  # each is (frame, x_pos, width, name, exon_num, colour)
    gene_exons = defaultdict(list)
    frames = []

    # collect all landmark items
    for lm in landmarks_sorted:
        frame = lm.get('frame', 0)
        colour = 'white'
        start = lm['start']
        end = lm['end']
        if end <= start:
            continue
        x_pos = start + xoffset
        width = end - start
        name = lm.get('name')
        exon_num = lm.get('exon', 1)
        items.append((frame, x_pos, width, name, exon_num, colour))
        gene_exons[name].append((frame, x_pos, width, name, exon_num, colour))
        if frame not in frames:
            frames.append(frame)

    frames.sort()

    # build connectors: connect exon N to exon N+1 for each gene
    connectors = []  # tuples (ex1_item, ex2_item, colour)
    for name, exlist in gene_exons.items():
        # sort exons by exon_num
        exlist_sorted = sorted(exlist, key=lambda e: e[4])
        for i in range(len(exlist_sorted) - 1):
            e1 = exlist_sorted[i]
            e2 = exlist_sorted[i+1]
            # ensure multi-exon
            if e2[4] > e1[4]:
                connectors.append((e1, e2, e1[5]))

    # dimensions
    row_h = height * 2
    font_size = max(8, int(row_h * 0.7))
    gap = 10

    # a single drawer that draws all exons at different y-rows and connectors
    class _MultiRowDrawer:
        def __init__(self, items, connectors, row_h, gap):
            self.items = items
            self.connectors = connectors
            self.row_h = row_h
            self.gap = gap
            # total height over all frame rows
            self.h = len(frames) * row_h + (len(frames)-1) * gap
            # width covers all items
            self.w = max((x + w for (_, x, w, _, _, _) in items), default=0)

        def draw(self, x=0, y=0, xscale=1.0):
            g = draw.Group(transform=f"translate({x} {y})")

            # helper to get y offset (flip so frame 0 is top)
            def y_offset(frame):
                idx = frames.index(frame)
                # inverted: highest frame at bottom
                max_idx = len(frames) - 1
                return (max_idx - idx) * (self.row_h + self.gap)

            # draw connectors routing from exon to exon based on vertical positions
            for e1, e2, colour in self.connectors:
                colour = 'black'
                f1, x1, w1, *_ = e1
                f2, x2, w2, *_ = e2
                # compute scaled positions
                x1_start = x1 * xscale
                x2_start = x2 * xscale
                w1_scaled = w1 * xscale
                w2_scaled = w2 * xscale
                # thickness of connector
                thickness = max(1, int(self.row_h * 0.05))
                # exon vertical bounds and mid-gap y-coordinate
                yA_top = y_offset(f1)
                yA_bottom = yA_top + self.row_h
                yB_top = y_offset(f2)
                yB_bottom = yB_top + self.row_h
                y_gap = ((yA_bottom + yB_top) / 2) if yA_top < yB_top else ((yB_bottom + yA_top) / 2)
                # midpoints of exons
                xA_mid = x1_start + w1_scaled/2
                xB_mid = x2_start + w2_scaled/2
                # draw vertical from first exon to gap
                if yA_top < yB_top:
                    g.append(draw.Lines(xA_mid, yA_bottom,
                                       xA_mid, y_gap,
                                       stroke=colour, stroke_width=thickness))
                    # horizontal between exons
                    g.append(draw.Lines(xA_mid, y_gap,
                                       xB_mid, y_gap,
                                       stroke=colour, stroke_width=thickness))
                    # vertical to second exon
                    g.append(draw.Lines(xB_mid, y_gap,
                                       xB_mid, yB_top,
                                       stroke=colour, stroke_width=thickness))
                else:
                    g.append(draw.Lines(xB_mid, yB_bottom,
                                       xB_mid, y_gap,
                                       stroke=colour, stroke_width=thickness))
                    g.append(draw.Lines(xB_mid, y_gap,
                                       xA_mid, y_gap,
                                       stroke=colour, stroke_width=thickness))
                    g.append(draw.Lines(xA_mid, y_gap,
                                       xA_mid, yA_top,
                                       stroke=colour, stroke_width=thickness))
                # label at horizontal segment midpoint
                name = e1[3]
                x_label = (xA_mid + xB_mid) / 2
                y_label = y_gap + font_size * 0.5
                g.append(draw.Text(text=name, font_size=font_size,
                                   x=x_label, y=y_label,
                                   font_family='monospace', center=True, fill='black'))

            # draw exon boxes
            for frame, x_pos, width, name, exon_num, colour in self.items:
                y0 = y_offset(frame)
                x0 = x_pos * xscale
                w0 = width * xscale
                # gene rectangle
                g.append(draw.Rectangle(x0, y0, w0, self.row_h,
                                      fill=colour, stroke='black'))

                # label
                if exon_num > 1 or len(gene_exons[name]) > 1:
                    pass
                else:
                    label = name
                    # start font as float based on row height
                    font = font_size
                    # multiplicative shrink factor per iteration (e.g., 0.90 -> reduce by 10% each step)
                    shrink_factor = 0.90
                    # approximate monospace character width (pixels per font unit)
                    char_w = 0.6
                    padding = 2
                    avail = w0 - padding
                    while (font * char_w * len(label)) > avail:
                        font = font * shrink_factor
                    # vertical offset tuned to visually center text; use float font
                    g.append(draw.Text(text=label, font_size=font,
                                       x=x0 + w0/2, y=y0 + self.row_h/2,
                                       font_family='monospace', center=True, fill='black'))

            return g

    # add the combined overview drawer
    figure.add(_MultiRowDrawer(items, connectors, row_h, gap))


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
    def __init__(self, h=3, font_size=XAXIS_FONT_SIZE):
        self.a = START_POS + XOFFSET
        self.b = END_POS + XOFFSET
        self.w = END_POS + XOFFSET + 1500
        self.h = h
        self.color = 'black'
        self.font_size = font_size
        self.ticks = [i for i in range(1000, 10000, 1000)]

    def draw(self, x=0, y=0, xscale=1.0):
        h = self.h
        a = self.a * xscale
        b = self.b * xscale
        x = x * xscale
        font_size = self.font_size
        # the tick marks and their labels are placed relative to the font, so
        # that they stay put when the font is scaled for a printed page
        tick_length = -font_size
        label_offset = -2 * font_size
        title_offset = -3.5 * font_size

        d = draw.Group(transform="translate({} {})".format(x, y))
        d.append(draw.Rectangle(a, 0, b - a, h,
                                fill=self.color, stroke=self.color))

        for tick in self.ticks:
            label = str(tick)
            x_tick = (tick + XOFFSET) * xscale
            d.append(draw.Lines(x_tick, 0, x_tick, tick_length, stroke=self.color, stroke_width=h))
            d.append(Label(0, label, font_size=font_size, offset=label_offset).draw(x=x_tick))

        d.append(Label(0, 'Nucleotide Position', font_size=font_size, offset=title_offset).draw(x=a + (b - a) / 2))

        return d


class LegendAndPercentages:
    def __init__(self, defect_percentages, highlighted, total_samples, lineheight, xaxisheight, force_move_percentages=False, with_legend=True, font_size=SIDEBAR_FONT_SIZE):
        self.a = START_POS + XOFFSET
        self.b = END_POS + XOFFSET
        self.font_size = font_size
        # the figure is as wide as the x axis, which leaves room to the right
        # of the plot for this sidebar to hang into
        self.w = XAxis().w
        self.defect_types = defect_percentages.keys()
        self.highlighted_types = highlighted
        self.defect_percentages = defect_percentages
        self.num_samples = total_samples
        # number of legend lines (3 columns)
        self.num_lines = (len(self.defect_types) + len(self.highlighted_types)) / 3
        # without a legend this element is just the percentage sidebar, which
        # hangs off the sample tracks and needs no room of its own
        self.h = 20 * self.num_lines if with_legend else 0
        self.lineheight = lineheight
        self.xaxisheight = xaxisheight
        # if True, move percentages into legend (used when any category is small)
        self.force_move_percentages = force_move_percentages
        # a page draws one legend for all plots, so this element can be asked
        # for the percentage sidebar only
        self.with_legend = with_legend

    def add_legend(self, a, column_space, barlen, barheight, drawing, include_percentages=False):
        """Draw legend entries. If include_percentages is True, append percentages to legend labels
        instead of drawing them in the sidebar."""
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

            # Build label text. If asked, include percentage next to defect name
            if include_percentages:
                pct = self.defect_percentages.get(defect, 0.0)
                # Only show percentage for defects that have an entry in defect_percentages
                if defect in self.defect_percentages:
                    label_text = f"{defect} ({round(pct, 1)}%)"
                else:
                    label_text = defect
            else:
                label_text = defect

            # place label to the right of the colored bar with a padding and left-aligned text
            label_padding = 12
            label_x = xpos + barlen + label_padding
            # vertical position: center text alongside the color bar (small upward offset)
            label_y = ypos + barheight / 2 - 5
            drawing.append(draw.Text(text=label_text,
                                     font_size=15,
                                     x=label_x,
                                     y=label_y,
                                     font_family='monospace',
                                     fill='black'))

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
        fontsize = self.font_size

        # Determine whether to move percentages into the legend
        # move_percentages_to_legend is controlled externally via force_move_percentages flag
        move_percentages_to_legend = bool(self.force_move_percentages)

        d = draw.Group(transform="translate({} {})".format(x, y))

        # On a page the sample count is already printed under the plot title, so
        # the "Seq." / "N=" axis labels would only repeat it.
        if self.with_legend:
            d.append(Label(-10, "Seq.", font_size=20, offset=yaxis_label_height + 12).draw(x=(a - 30)))
            d.append(Label(-10, f"N={self.num_samples}", font_size=20, offset=yaxis_label_height - 12).draw(x=(a - 30)))

            # draw legend; optionally include percentages in the legend labels
            self.add_legend(a, column_space, barlen, barheight, d,
                            include_percentages=move_percentages_to_legend)

        # only draw the sidebar when percentages are not moved into the legend.
        # A page has one legend for all plots, so its percentages always go into
        # the sidebar, however small the categories are.
        if self.with_legend and move_percentages_to_legend:
            return d
        if not self.defect_types:
            return d
        self.add_sidebar(sidebar_x, sidebar_ystart, fontsize, d)

        return d


class PlotTitle:
    """A title drawn above a plot, with an optional sample count underneath"""
    def __init__(self, text, samples=None, font_size=TITLE_FONT_SIZE,
                 sub_font_size=SUBTITLE_FONT_SIZE):
        self.text = str(text)
        self.samples = samples
        self.font_size = font_size
        self.sub_font_size = sub_font_size
        # the block is a bit taller than its text, so the two lines do not
        # collide and the title does not touch the sample tracks
        self.h = 1.6 * font_size
        if samples is not None:
            self.h += 1.6 * sub_font_size
        # match the width of the widest element so the title is centered on the
        # plot area rather than on the page
        self.w = XAxis().w

    def draw(self, x=0, y=0, xscale=1.0):
        d = draw.Group(transform="translate({} {})".format(x, y))
        center_x = self.w * xscale / 2
        # y grows upwards inside this inverted context, so the title takes the
        # top of the block and the sample count sits on the line below it
        title_y = self.h - 0.8 * self.font_size
        d.append(draw.Text(self.text, self.font_size,
                           center_x, title_y,
                           font_family='monospace',
                           text_anchor='middle',
                           fill='black'))
        if self.samples is not None:
            d.append(draw.Text(f'N={self.samples}', self.sub_font_size,
                               center_x, title_y - self.font_size - 6,
                               font_family='monospace',
                               text_anchor='middle',
                               fill='black'))
        return d


class SharedLegend:
    """
    A single legend for a page holding several plots.

    Entries are laid out in columns and the whole block is centered on the page,
    below all plots.
    """
    ROW_HEIGHT = 20
    FONT_SIZE = 15
    BAR_HEIGHT = 10
    # the gap between two entries of a turned legend
    LEGEND_ENTRY_GAP = 10
    # the gap between the swatch of a turned entry and its label
    LEGEND_LABEL_GAP = 10
    # how deep a label is across the page, as a multiple of the font size: the
    # band of glyphs that has to line up with the swatch it belongs to
    LABEL_BAND_FACTOR = 0.7
    # how wide one character of a monospace label is, as a multiple of the font
    # size; it is what a label is measured with, since nothing here can measure
    # real text
    CHAR_WIDTH_FACTOR = 0.6
    # the sizes above are the ones for a 15px font; anything else scales from
    # here
    FONT_SIZE_DEFAULT = 15

    def __init__(self, defect_types, highlighted_types, num_columns=3,
                 bar_width=60, padding=16, font_size=None):
        self.entries = list(defect_types) + list(highlighted_types)
        self.num_columns = max(1, num_columns)
        self.bar_width = bar_width
        self.padding = padding
        if font_size:
            self.FONT_SIZE = font_size
            # keep the row tall enough for the text it holds
            self.ROW_HEIGHT = self.ROW_HEIGHT * font_size / self.FONT_SIZE_DEFAULT
            self.BAR_HEIGHT = self.BAR_HEIGHT * font_size / self.FONT_SIZE_DEFAULT
        num_rows = ceil(len(self.entries) / self.num_columns)
        self.h = max(1, num_rows) * self.ROW_HEIGHT + self.padding
        # column width: bar + gap + widest label
        widest = max((len(e) for e in self.entries), default=0)
        label_width = widest * self.label_length('') + 20
        self.column_width = self.bar_width + 12 + label_width
        self.w = self.num_columns * self.column_width

    def label_length(self, entry):
        """How far a label runs along its baseline."""
        return len(entry) * self.FONT_SIZE * self.CHAR_WIDTH_FACTOR

    def turned_entry_band(self):
        """
        How deep one turned entry is across the page.

        A turned entry is a swatch with its label on the same vertical line, so
        the band is as deep as the deeper of the two, and the shallower one sits
        in the middle of it.
        """
        return max(self.BAR_HEIGHT, self.LABEL_BAND_FACTOR * self.FONT_SIZE)

    def turned_entry_pitch(self):
        """How far apart two turned entries sit across the page."""
        return self.turned_entry_band() + self.LEGEND_ENTRY_GAP

    def turned_size(self):
        """
        The (width, height) of the block that draw_rotated draws.

        Turning the legend swaps the two: the entries march across the page
        instead of down it, and the block is as deep as a turned entry, which is
        the label above its swatch, plus padding at either end.
        """
        entries = [e for e in self.entries if self.color_of(e) is not None]
        band = self.turned_entry_band()
        width = (2 * self.padding
                 + (len(entries) - 1) * self.turned_entry_pitch() + band)
        longest = max((self.label_length(e) for e in entries), default=0)
        height = (2 * self.padding + self.bar_width + self.LEGEND_LABEL_GAP
                  + longest)
        return width, height

    @staticmethod
    def color_of(entry):
        """The swatch color of a legend entry, or None when there is none."""
        if entry in DEFECT_TO_COLOR:
            return DEFECT_TO_COLOR[entry]
        if entry in HIGHLIGHT_COLORS:
            return HIGHLIGHT_COLORS[entry]
        print(f"No color defined for defect {entry}")
        return None

    def draw(self, x=0, y=0, xscale=1.0):
        """Draw the legend as a horizontal block below its origin."""
        d = draw.Group(transform="translate({} {})".format(x, y))
        num_per_column = ceil(len(self.entries) / self.num_columns)
        for i, entry in enumerate(self.entries):
            color = self.color_of(entry)
            if color is None:
                continue
            column = i // num_per_column
            row = i % num_per_column
            xpos = column * self.column_width
            ypos = self.padding + row * self.ROW_HEIGHT
            d.append(draw.Rectangle(xpos, ypos, self.bar_width,
                                    self.BAR_HEIGHT, fill=color, stroke=color))
            d.append(draw.Text(entry, self.FONT_SIZE,
                               xpos + self.bar_width + 12,
                               ypos + self.BAR_HEIGHT / 2 - 2,
                               font_family='monospace',
                               fill='black'))
        return d

    def draw_rotated(self):
        """
        Draw the legend turned a quarter turn counter-clockwise, so that it
        reads from the bottom up and its entries march across the page.

        Every entry is turned as a whole, so the swatch of an entry and its
        label stay together: the label sits above its swatch, on the same
        vertical line. The swatches are all bottom aligned, so the entries read
        as one row of colours with their names above them.

        The block is turned_size() wide and tall, measured from its bottom left
        corner, with y counting up the page: the page flips every y it is
        handed. A legend with one column is what usually goes into a free
        corner, because then it is about as wide as it is deep.
        """
        d = draw.Group()
        band = self.turned_entry_band()
        label_band = self.LABEL_BAND_FACTOR * self.FONT_SIZE
        entries = [e for e in self.entries if self.color_of(e) is not None]
        for i, entry in enumerate(entries):
            color = self.color_of(entry)
            xpos = self.padding + i * self.turned_entry_pitch()
            # the swatch and its label share the band of the entry, each
            # centered in it so that both sit on the same vertical line
            d.append(draw.Rectangle(xpos + (band - self.BAR_HEIGHT) / 2,
                                    self.padding,
                                    self.BAR_HEIGHT, self.bar_width,
                                    fill=color, stroke=color))
            # The label reads upwards, so it starts above its swatch and runs
            # from there. Turned, the glyphs of a text sit to the left of its
            # baseline, so the baseline is half the band past the start of the
            # band. The page flips every y it is handed, so the rotation has
            # to be about the flipped position.
            tx = xpos + (band + label_band) / 2
            ty = self.padding + self.bar_width + self.LEGEND_LABEL_GAP
            d.append(draw.Text(entry, self.FONT_SIZE, tx, ty,
                               text_anchor='start',
                               transform="rotate(-90 {} {})".format(tx, -ty),
                               font_family='monospace',
                               fill='black'))
        return d


class ProviralLandscapePlot:
    def __init__(self, figure, tot_samples, lineheight=None,
                 title_font_size=TITLE_FONT_SIZE,
                 subtitle_font_size=SUBTITLE_FONT_SIZE,
                 axis_font_size=XAXIS_FONT_SIZE,
                 sidebar_font_size=SIDEBAR_FONT_SIZE):
        self.curr_samp_name = ''
        self.defects = set()
        self.figure = figure
        self.curr_multitrack = []
        self.tot_samples = tot_samples
        if lineheight is None:
            lineheight = 500 / self.tot_samples if self.tot_samples > 0 else 0
            if lineheight > 5:
                lineheight = 5
        self.lineheight = lineheight
        self.xaxisheight = 0
        self.title_font_size = title_font_size
        self.subtitle_font_size = subtitle_font_size
        self.axis_font_size = axis_font_size
        self.sidebar_font_size = sidebar_font_size

    def add_line(self, samp_name, xstart, xend, defect_type, highlight):
        if defect_type not in DEFECT_TO_COLOR.keys():
            print(f"Unknown defect: {defect_type}")
            return
        if samp_name != self.curr_samp_name:
            if self.curr_samp_name != '':
                self.draw_current_multitrack()
            self.curr_samp_name = samp_name
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
            self.figure.add(Multitrack(self.curr_multitrack), gap=SAMPLE_GAP)
        self.curr_multitrack = []

    def add_xaxis(self):
        font_size = self.axis_font_size
        padding = 0.5 * font_size
        gap = 2.5 * font_size
        xaxis_thickness = 0.15 * font_size
        self.figure.add(XAxis(h=xaxis_thickness, font_size=font_size),
                        padding=padding, gap=gap)
        self.xaxisheight = padding + gap + xaxis_thickness

    def legends_and_percentages(self, defect_percentages, highlight_types,
                                force_move_percentages=False, with_legend=True):
        self.figure.add(LegendAndPercentages(defect_percentages,
                                             highlight_types,
                                             self.tot_samples,
                                             self.lineheight,
                                             self.xaxisheight,
                                             force_move_percentages,
                                             with_legend,
                                             self.sidebar_font_size))


def sort_csv_lines(lines):
    lines.sort(key=lambda elem: defect_order(elem['defect'].strip()))
    for _, defect_rows in groupby(lines, key=lambda elem: DEFECT_TYPE[elem['defect']]):
        defect_rows = list(defect_rows)
        defect_rows.sort(key=lambda elem: elem['samp_name'].strip())
        all_rows_by_sample = []
        for _, samp_rows in groupby(defect_rows, itemgetter('samp_name')):
            samp_rows = list(samp_rows)
            samp_rows.sort(key=lambda elem: int(elem['ref_start'].strip()))
            if DEFECT_TYPE[samp_rows[0]['defect']] not in ["5' Defect"]:
                # We want to remove 50bp gaps, unless it's a 5'defect. Can also skip line defects
                for i, row in enumerate(samp_rows):
                    ref_start = int(row['ref_start'].strip())
                    ref_end = int(row['ref_end'].strip())
                    if is_truthy(row['is_inverted']) or is_truthy(row['is_defective']):
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


def free_grid_slots(num_plots, columns, num_rows):
    """
    The parts of a plot grid that hold no plot.

    Plots fill the grid from the top left, so what is left over is a run of
    cells at the end of the last row. Each slot is returned as (row, first
    column, number of columns), biggest and lowest first, so that a caller that
    needs one piece of free space gets the free corner of the grid.
    """
    occupied = {divmod(i, columns) for i in range(num_plots)}
    slots = []
    for row in range(num_rows):
        column = 0
        while column < columns:
            if (row, column) in occupied:
                column += 1
                continue
            first = column
            while column < columns and (row, column) not in occupied:
                column += 1
            slots.append((row, first, column - first))
    # the corner at the bottom of the page is the one worth having, and within
    # a row the rightmost run of cells is the one that reads as a corner
    slots.sort(key=lambda slot: (-slot[0], -slot[2], -slot[1]))
    return slots


def create_proviral_plot(input_file, output_svg, dpi=None):
    """
    Draw a single proviral landscape plot and write it to output_svg.

    input_file is an open file object or any iterable of csv dict rows.
    dpi, when given, writes a raster image instead of an svg; see save_raster().
    """
    lines = read_landscape_rows(input_file, source=getattr(input_file, 'name', 'input'))
    figure, _, _ = build_proviral_figure(lines, title=None)
    # display with a standard width so the overview is visible
    page = figure.show(w=PLOT_WIDTH)
    if dpi:
        save_raster(page, output_svg, dpi)
    else:
        page.save_svg(output_svg)


def create_proviral_page(csv_files, output_svg, columns=GRID_COLUMNS,
                         title_column=None, titles=None, legend_font_size=None,
                         page_size=DEFAULT_PAGE_SIZE, with_percentages=True,
                         dpi=None):
    """
    Draw one proviral landscape plot per input file onto a single page.

    csv_files : list of paths to proviral landscape csv files
    output_svg: path of the svg to write
    columns   : number of plots per row; the remaining plots wrap onto further
                rows
    title_column: csv column to take each plot's title from, e.g. 'sample' to
                title every plot after the participant it belongs to
    titles    : dict of title overrides, keyed by input file stem or by
                participant number; see parse_title_overrides()
    legend_font_size: font size of the shared legend (default 15)
    page_size : key of PAGE_SIZES_MM, or None to let the page grow to fit its
                content instead of matching a paper size
    with_percentages : draw the per-plot percentage sidebar
    dpi       : when given, write a raster image at this resolution instead of
                an svg; needs cairosvg (and pillow for tiff)

    Every plot is given the same height so that the proportions of the defect
    categories can be compared directly between plots. One legend is drawn for
    the whole page, centered below the plots, and every plot keeps its own
    percentage sidebar.
    """
    inputs = list(csv_files)
    if not inputs:
        raise ValueError("No input csv files given")
    missing = [path for path in inputs if not os.path.exists(path)]
    if missing:
        raise FileNotFoundError("Input csv file(s) not found: "
                                + ", ".join(missing))

    # read everything first, so the sample counts are known before we decide how
    # tall each sample track has to be
    rows_by_file = []
    sample_counts = []
    for path in inputs:
        lines = read_landscape_csv(path)
        rows_by_file.append(lines)
        sample_counts.append(count_samples(lines))

    num_rows = ceil(len(inputs) / columns)
    paper_w_mm, paper_h_mm = PAGE_SIZES_MM.get(page_size, (None, None))

    # How much of the paper one plot unit is worth. This is set by the width the
    # grid needs, and the height that leaves over then decides how many units of
    # sample tracks each plot gets. Working the height out first and dividing
    # into it means the layout fits the paper without any trial and error.
    grid_w_units = columns * PLOT_WIDTH + (columns - 1) * PLOT_GAP
    if paper_w_mm is None:
        unit = 1.0
        plot_gap = PLOT_GAP
        page_margin = PAGE_MARGIN
    else:
        unit = (paper_w_mm - 2 * PAGE_MARGIN_MM) / grid_w_units
        plot_gap = PLOT_GAP_MM
        page_margin = PAGE_MARGIN_MM
    # the shared legend is laid out in columns, one row per so many entries
    legend_columns = max(columns, 1)

    def legend_height_mm(num_entries):
        if num_entries <= 0:
            return LEGEND_PADDING_MM
        rows_needed = ceil(num_entries / legend_columns)
        return rows_needed * LEGEND_ROW_MM + LEGEND_PADDING_MM

    # Height left for the grid, once the margins and the legend strip are taken
    # out. Everything a plot needs other than its sample tracks is text, sized
    # in millimetres, so it does not change with the scale.
    def sample_block_units(legend_mm):
        if paper_w_mm is None:
            # no paper to fit: use the nominal block height
            return SAMPLE_BLOCK_HEIGHT
        available = (paper_h_mm - 2 * page_margin - legend_mm - PLOT_GAP_MM
                     - (num_rows - 1) * plot_gap)
        block_mm = available / num_rows - TITLE_CHROME_MM - XAXIS_CHROME_MM
        return max(block_mm / unit, 0)

    # Every plot gets the same room for its sample tracks: a plot with many
    # samples simply gets thinner tracks than a plot with few. Each sample also
    # costs a fixed gap, so that has to come out of the same budget, otherwise
    # plots with more samples end up taller.
    def block_height_for(legend_mm):
        block = sample_block_units(legend_mm)
        if sample_counts:
            needed = max(sample_counts) * (MIN_LINEHEIGHT + SAMPLE_GAP)
            if needed > block:
                block = needed
        return block

    # Text is sized in millimetres on the page, so the font sizes handed to the
    # figures are those millimetres expressed in plot units.
    if paper_w_mm is None:
        font_sizes = (TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE,
                      XAXIS_FONT_SIZE, SIDEBAR_FONT_SIZE)
        legend_font_size = (legend_font_size if legend_font_size is not None
                            else SharedLegend.FONT_SIZE)
    else:
        font_sizes = tuple(size_mm / unit for size_mm in
                           (TITLE_FONT_MM, SUBTITLE_FONT_MM,
                            XAXIS_FONT_MM, SIDEBAR_FONT_MM))
        # an explicit --legend-font-size is in plot units like it always was;
        # without one, use a sensible size on the paper
        legend_font_size = (legend_font_size if legend_font_size is not None
                            else LEGEND_FONT_MM / unit)

    def build_figures(block_height):
        """Build one figure per input file, all with the given track budget."""
        built = []
        highlighted_types = set()
        defect_types = []
        for path, lines, num_samples in zip(inputs, rows_by_file, sample_counts):
            if num_samples > 0:
                lineheight = block_height / num_samples - SAMPLE_GAP
                if lineheight < 0:
                    lineheight = 0
            else:
                lineheight = 0
            figure, defects, highlighted = build_proviral_figure(
                lines,
                title=title_for_plot(path, lines, title_column, titles),
                lineheight=lineheight,
                with_legend=False,
                with_percentages=with_percentages,
                font_sizes=font_sizes,
            )
            built.append(figure)
            highlighted_types |= highlighted
            for defect in defects:
                if defect not in defect_types:
                    defect_types.append(defect)
        return built, defect_types, highlighted_types

    def make_legend(defect_types, highlighted_types, num_columns=None):
        return SharedLegend(sorted(defect_types, key=defect_type_order),
                            sorted(highlighted_types),
                            num_columns=(legend_columns if num_columns is None
                                         else num_columns),
                            font_size=legend_font_size)

    # Where the legend goes. The strip below the grid always works, but a grid
    # whose last row is not full has an empty corner, and a legend turned on
    # its side fits in a corner of a single plot, which is nicer: the plots get
    # the whole height of the paper, and nothing overlaps anything.
    #
    # A turned legend is as wide as the horizontal one is tall, so it is built
    # with a single column, and it is measured against the free cells the grid
    # leaves over. When no corner is big enough the strip below the grid is
    # used after all.
    def corner_legend_slot():
        """
        Find a free corner of the grid that a turned legend fits into.

        Returns (row, first column, column count, legend, track budget of the
        plots), or None when the grid is full or every corner is too small.
        """
        # without a strip below it, the plots can have the whole paper height
        block_height = block_height_for(0)
        corner_figures, defect_types, highlighted_types = build_figures(
            block_height)
        legend = make_legend(defect_types, highlighted_types, num_columns=1)
        turned_w, turned_h = legend.turned_size()
        panel_h = max(figure.h for figure in corner_figures)
        # the corner gap keeps the legend clear of the plots around it
        margin = ((LEGEND_CORNER_GAP_MM if paper_w_mm is not None
                   else PLOT_GAP / 2) / unit)
        for row, column, span in free_grid_slots(len(inputs), columns,
                                                 num_rows):
            slot_w = span * PLOT_WIDTH + (span - 1) * (plot_gap / unit)
            if (turned_w + 2 * margin <= slot_w
                    and turned_h + 2 * margin <= panel_h):
                return row, column, span, legend, block_height
        return None

    corner = corner_legend_slot()
    if corner is not None:
        _, _, _, legend, block_height = corner
        figures, defect_types, highlighted_types = build_figures(block_height)
        legend_in_corner = True
    else:
        # The legend depends on which defects the plots turned out to hold, and
        # how tall each plot is depends on how much room the legend leaves, so
        # build once to find out, then build again for real.
        worst_case_entries = len(DEFECT_TO_COLOR) + len(HIGHLIGHT_COLORS)
        block_height = block_height_for(legend_height_mm(worst_case_entries))
        figures, defect_types, highlighted_types = build_figures(block_height)
        legend = make_legend(defect_types, highlighted_types)
        block_height = block_height_for(legend_height_mm(len(legend.entries)))
        figures, defect_types, highlighted_types = build_figures(block_height)
        legend = make_legend(defect_types, highlighted_types)
        legend_in_corner = False

    # A sample can show up under more than one defect category, so a plot can
    # come out a track or two taller than planned. Pad the shorter plots with a
    # blank track, so that every plot is exactly the same height.
    panel_h_units = max(figure.h for figure in figures)
    for figure in figures:
        missing = panel_h_units - figure.h
        if missing > 0:
            figure.add(Multitrack([Track(START_POS + XOFFSET,
                                          START_POS + XOFFSET,
                                          color='#ffffff', h=missing)]),
                       gap=0)

    # a common horizontal scale keeps plots directly comparable
    xscale = PLOT_WIDTH / max(figure.w for figure in figures)

    # Position everything in millimetres of paper. The drawing declares that
    # physical size, so it prints, or rasterizes, at exactly the right
    # dimensions whatever resolution is asked for. Without a paper size the page
    # stays in plot units and simply grows to fit.
    # A legend that goes into a free corner of the grid takes no room below the
    # grid at all, so only the strip below the grid counts towards the height
    # of the content.
    legend_h_mm = (0.0 if legend_in_corner
                   else (legend_height_mm(len(legend.entries))
                         if paper_w_mm is not None else legend.h))
    content_w_mm = grid_w_units * unit
    content_h_mm = (num_rows * panel_h_units * unit
                    + (num_rows - 1) * plot_gap + PLOT_GAP_MM + legend_h_mm)
    if paper_w_mm is None:
        page_w = grid_w_units
        page_h = (num_rows * panel_h_units + (num_rows - 1) * PLOT_GAP
                  + legend_h_mm)
        grid_left = 0.0
        grid_top = 0.0
    else:
        page_w = paper_w_mm
        page_h = paper_h_mm
        grid_left = (page_w - content_w_mm) / 2
        grid_top = (page_h - content_h_mm) / 2

    page = draw.Drawing(page_w, page_h, origin=(0, 0),
                        context=draw.Context(invert_y=True))
    if paper_w_mm is not None:
        # declare the physical size; the viewBox is in millimetres
        page.svg_args = {'width': f'{page_w:g}mm', 'height': f'{page_h:g}mm'}

    # The page flips the y axis of everything drawn into it, so a block that is
    # drawn downwards from its origin ends up above that origin. Content is
    # therefore placed by its bottom edge: a distance measured downwards from
    # the top of the page becomes (distance - page_h), and the block hangs
    # upwards from there.
    def from_top(distance):
        return distance - page_h

    # Each figure is drawn in plot units inside a group scaled onto the page, so
    # that the tracks, the gaps and the fonts all scale together.
    panel_w_mm = PLOT_WIDTH * unit
    panel_h_mm = panel_h_units * unit
    for i, figure in enumerate(figures):
        row, column = divmod(i, columns)
        x = grid_left + column * (panel_w_mm + plot_gap)
        row_top = grid_top + row * (panel_h_mm + plot_gap)
        # center the plot vertically in its row
        figure_top = row_top + (panel_h_mm - figure.h * unit) / 2
        # a figure is drawn above the group's origin, one figure height tall
        group = draw.Group(transform="translate({} {}) scale({})".format(
            x, from_top(figure_top + figure.h * unit), unit))
        for y_local, element in figure.elements:
            group.append(element.draw(xscale=xscale, y=y_local - figure.h))
        page.append(group)

    if legend_in_corner:
        # A turned legend in the free corner of the grid: its width and height
        # are the other way round from the horizontal one, and it is centered
        # across the cells no plot was put in. Its lowest point sits on the
        # lowest point of the plots of that row, which is the bottom of the
        # row as far as the drawn axis title reaches below it.
        row, column, span = corner[:3]
        slot_left = grid_left + column * (panel_w_mm + plot_gap)
        slot_w_mm = span * panel_w_mm + (span - 1) * plot_gap
        slot_top = grid_top + row * (panel_h_mm + plot_gap)
        turned_w_mm, turned_h_mm = (size * unit
                                    for size in legend.turned_size())
        axis_font = (XAXIS_FONT_MM if paper_w_mm is not None
                     else XAXIS_FONT_SIZE * unit)
        legend_x = slot_left + (slot_w_mm - turned_w_mm) / 2
        legend_bottom = (slot_top + panel_h_mm
                         + AXIS_OVERHANG_FACTOR * axis_font)
        legend_group = draw.Group(transform="translate({} {}) scale({})".format(
            legend_x, from_top(legend_bottom), unit))
        legend_group.append(legend.draw_rotated())
    else:
        # The shared legend sits below the grid, separated by the gap the height
        # budget reserved for it. Measuring from the grid rather than from the
        # bottom of the page keeps the two from overlapping when the content
        # does not fill the paper exactly.
        grid_h_mm = num_rows * panel_h_units * unit + (num_rows - 1) * plot_gap
        legend_top = grid_top + grid_h_mm + PLOT_GAP_MM
        legend_x = (page_w - legend.w * unit) / 2
        legend_group = draw.Group(transform="translate({} {}) scale({})".format(
            legend_x, from_top(legend_top + legend_h_mm), unit))
        legend_group.append(legend.draw())
    page.append(legend_group)

    if dpi:
        save_raster(page, output_svg, dpi)
    else:
        page.save_svg(output_svg)


def save_raster(page, output_path, dpi):
    """
    Write a drawing out as a raster image, choosing the format from the file
    extension: .png, .tiff/.tif, or anything else falls back to png.

    The drawing declares its physical size in millimetres, so dpi is what
    decides the pixel dimensions; 300 is what most journals ask for.
    """
    try:
        import cairosvg
    except ImportError:
        raise ImportError(
            'writing ' + os.path.splitext(output_path)[1].lstrip('.') +
            ' needs cairosvg; install it with: uv pip install cairosvg pillow')

    extension = os.path.splitext(output_path)[1].lower()
    wants_tiff = extension in ('.tif', '.tiff')
    png = cairosvg.svg2png(bytestring=page.as_svg().encode('utf-8'), dpi=dpi)

    if not wants_tiff:
        with open(output_path, 'wb') as output_file:
            output_file.write(png)
        return

    try:
        from PIL import Image
    except ImportError:
        raise ImportError(
            'writing tiff needs pillow; install it with: uv pip install pillow')

    import io
    # LZW keeps a large, flat-colour figure small without any loss, and the
    # resolution tags stop the image being placed at the wrong physical size
    image = Image.open(io.BytesIO(png))
    image.save(output_path, format='TIFF', compression='tiff_lzw',
               dpi=(dpi, dpi))


def read_landscape_rows(input_file, source='input'):
    """
    Turn an open csv file (or any iterable of raw csv lines) into a list of rows.

    Handles the two things that spreadsheet exports add and hand written csvs
    get wrong: a utf-8 byte order mark and whitespace around the header names.
    Rows without a sample name (blank trailing lines, stray separators) are
    dropped.
    """
    if hasattr(input_file, 'read'):
        input_file = input_file.read()
    if isinstance(input_file, (str, bytes)):
        if isinstance(input_file, bytes):
            input_file = input_file.decode('utf-8-sig')
        elif input_file.startswith('\ufeff'):
            input_file = input_file.lstrip('\ufeff')
        input_file = input_file.splitlines()
    if all(isinstance(row, dict) for row in input_file):
        # already parsed rows
        return [dict(row) for row in input_file]

    reader = DictReader(input_file)
    # ' samp_name' from a padded header would otherwise silently drop every row
    reader.fieldnames = [name.strip() if name else name
                         for name in (reader.fieldnames or [])]
    missing = [column for column in REQUIRED_COLUMNS
               if column not in reader.fieldnames]
    if missing:
        raise ValueError(
            "{} is missing the required column(s): {}".format(
                source, ", ".join(missing)))

    rows = []
    for row in reader:
        # a short final line yields None for the columns it did not reach
        row = {key: (value if value is not None else '')
               for key, value in row.items()}
        if row['samp_name'].strip():
            rows.append(row)
    return rows


def read_landscape_csv(path):
    """
    Read a proviral landscape csv file into a list of rows.
    """
    with open(path, 'r', encoding='utf-8-sig', newline='') as input_file:
        return read_landscape_rows(input_file, source=path)


def count_samples(lines):
    """Number of distinct samples in a list of csv rows"""
    return len(set(r['samp_name'].strip() for r in lines
                   if r['defect'].strip() in DEFECT_TYPE))


def defect_type_order(defect_type):
    """Sort key that puts defect types in the order they are drawn in"""
    try:
        return DEFECT_ORDER[defect_type]
    except KeyError:
        return max(DEFECT_ORDER.values()) + 1


def plot_title(path, lines=None, title_column=None):
    """
    Derive a plot title for one input file.

    With title_column given (the name of a column in the csv, typically the
    first one) the title is taken from that column instead of from the file
    name: the participant number every sample name starts with, so a plot is
    titled after the participant rather than after whatever the file happens
    to be called. Falls back to the file name when the column is missing or
    when the sample names do not agree on one prefix.
    """
    if title_column and lines:
        title = participant_id(lines, title_column)
        if title:
            return title
    return os.path.splitext(os.path.basename(path))[0]


def participant_id(lines, column='sample'):
    """
    The leading participant number that every sample name in lines shares.

    Sample names look like ``0380X00415ANFL11M11-NFLHIVDNA_S158``, so the
    participant number is the first four digits (optionally behind a letter).
    Sample names that do not look like that at all (controls such as
    ``HIV3644NS2`` are named differently within one participant's file) are
    skipped. Returns None when the column is absent or when the sample names
    that do look like participant names disagree, since a title has to be
    unambiguous.
    """
    prefixes = set()
    for row in lines:
        value = (row.get(column) or '').strip()
        if not value:
            continue
        match = PARTICIPANT_PATTERN.match(value)
        if match:
            prefixes.add(match.group(1))
    if len(prefixes) == 1:
        return prefixes.pop()
    return None


def parse_title_overrides(spec):
    """
    Turn a ``0913=BC023,0380=BC016`` command line string into a dict.

    Keys are matched against the file name stem first and then against the
    participant number taken from the csv, so the mapping can be written
    either way.
    """
    overrides = {}
    if not spec:
        return overrides
    for item in spec.split(','):
        item = item.strip()
        if not item:
            continue
        if '=' not in item:
            raise ValueError(
                f"not a key=value title: '{item}' (expected e.g. 0913=BC023)")
        key, _, title = item.partition('=')
        key = key.strip()
        if not key or not title.strip():
            raise ValueError(
                f"not a key=value title: '{item}' (expected e.g. 0913=BC023)")
        overrides[key] = title.strip()
    if not overrides:
        raise ValueError("no key=value titles given")
    return overrides


def title_for_plot(path, lines, title_column=None, overrides=None):
    """
    Resolve the title of a single plot: an explicit override wins, then the
    title column of the csv, then the input file name.
    """
    if overrides:
        stem = os.path.splitext(os.path.basename(path))[0]
        if stem in overrides:
            return overrides[stem]
        # input files are commonly named after the participant
        # (proviral_landscape_3641.csv), which is also a usable key
        for number in re.findall(r'\d{4}', stem):
            if number in overrides:
                return overrides[number]
        # a bare key like 0913 should work even without --title-column, so
        # fall back to the usual participant columns
        for column in ([title_column] if title_column else []) + ['sample',
                                                                   'samp_name']:
            participant = participant_id(lines, column)
            if participant in overrides:
                return overrides[participant]
    return plot_title(path, lines, title_column)


def build_proviral_figure(lines, title=None, lineheight=None, with_legend=True,
                            with_percentages=True, font_sizes=None):
    """
    Build the Figure for a single proviral landscape plot.

    lines            : list of csv dict rows
    title            : optional title drawn above the plot
    lineheight       : height of a single sample track; when given, every plot
                       can be given the same value so that plots on a shared
                       page have the same height
    with_legend      : whether to draw this plot's own legend. When plotting
                       several inputs on one page a shared legend is drawn
                       instead, so pass False.
    with_percentages : whether to draw the percentage sidebar. Pass False only
                       to get a bare plot.
    font_sizes    : (title, subtitle, axis, sidebar) font sizes in plot units.
                       A page scales the figures onto the paper, so it passes
                       sizes that come out the right physical size there.

    Returns (figure, defect_types, highlighted_types).
    """
    if font_sizes is None:
        font_sizes = (TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE,
                      XAXIS_FONT_SIZE, SIDEBAR_FONT_SIZE)

    # set up figure and counters
    # total unique samples (across all defects)
    total_samples = len(set(r['samp_name'].strip() for r in lines if r['defect'].strip() in DEFECT_TYPE))
    figure = Figure()
    plot = ProviralLandscapePlot(figure, total_samples, lineheight=lineheight,
                                 title_font_size=font_sizes[0],
                                 subtitle_font_size=font_sizes[1],
                                 axis_font_size=font_sizes[2],
                                 sidebar_font_size=font_sizes[3])
    # the title comes first so that it ends up above everything else
    if title:
        figure.add(PlotTitle(str(title), samples=total_samples or None,
                             font_size=plot.title_font_size,
                             sub_font_size=plot.subtitle_font_size),
                   gap=10)
    
    # keep raw counts while building percentages later
    defect_counts = defaultdict(int)
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
                if is_truthy(row['is_inverted']):
                    highlighted_set.add('Inverted Region')
                    highlighted = 'Inverted Region'
                if is_truthy(row['is_defective']):
                    # TODO: incorporate this when we get ranges info from proviral.
                    # highlighted_set.add('Defect Region')
                    # highlighted = 'Defect Region'
                    pass
                plot.add_line(samp, xstart, xend, defect, highlighted)
        # count samples in this defect for percentages
        defect_counts[defect] += len(sample_order)

    # convert counts to percentages (only include defects that have a defined color)
    defect_percentages = defaultdict(int)
    for defect, number in defect_counts.items():
        if defect not in DEFECT_TO_COLOR:
            continue
        defect_percentages[defect] = number / total_samples * 100

    # Determine whether to move percentages into the legend based on adjacency in the
    # right-hand percentage sidebar. The sidebar iterates defects in the same order
    # as defect_percentages.keys(), so use that ordering here.
    neighbour_flag = False
    sidebar_entries = list(defect_percentages.keys())
    total_entries = len(sidebar_entries)
    if total_entries > 1:
        # build list of counts for sidebar entries (0 if missing)
        counts_list = [defect_counts.get(entry, 0) for entry in sidebar_entries]
        for i in range(total_entries - 1):
            c1 = counts_list[i]
            c2 = counts_list[i + 1]
            # both must be active (count>0) and both have very few samples (<4)
            if c1 > 0 and c2 > 0 and c1 < 4 and c2 < 4:
                neighbour_flag = True
                break

    # finalize plot
    plot.draw_current_multitrack()
    plot.add_xaxis()
    if with_percentages:
        plot.legends_and_percentages(defect_percentages, highlighted_set,
                                     force_move_percentages=neighbour_flag,
                                     with_legend=with_legend)
    return figure, set(plot.defects), highlighted_set


def main(argv=None):
    parser = ArgumentParser(
        description="Draw proviral landscape plots, one per input csv, onto a "
                    "single SVG page.")
    parser.add_argument("proviral_landscape_csvs", nargs='+',
                        help="Proviral landscape input file(s), produced by the "
                             "proviral pipeline. One plot is drawn per file. "
                             "The output file must be given last.")
    parser.add_argument("output_svg",
                        help="Output SVG (always the last argument)")
    parser.add_argument("-c", "--columns", type=int, default=GRID_COLUMNS,
                        help=f"Number of plots per row (default: {GRID_COLUMNS})")
    parser.add_argument("--title-column", metavar="COLUMN",
                        help="Take each plot's title from this csv column "
                             "(e.g. sample) instead of from the input file "
                             "name. Only the participant number every sample "
                             "name in that file starts with is used.")
    parser.add_argument("--legend-font-size", type=int, metavar="PX",
                        help=f"Font size of the shared legend "
                             f"(default: {SharedLegend.FONT_SIZE})")
    parser.add_argument("--titles", metavar="KEY=TITLE[,KEY=TITLE...]",
                        help="Explicit plot titles. KEY is either the input "
                             "file stem (proviral_landscape_0913) or the "
                             "participant number (0913); it wins over "
                             "--title-column. Example: "
                             "--titles 0913=BC023,0380=BC016")
    parser.add_argument("--page-size", choices=[*PAGE_SIZES_MM, 'fit'],
                        default=DEFAULT_PAGE_SIZE,
                        help="Paper size the page is laid out for (default: "
                             f"{DEFAULT_PAGE_SIZE}). The drawing declares this "
                             "physical size, so it prints and rasterizes at it. "
                             "Use 'fit' to let the page grow to fit its "
                             "content instead.")
    parser.add_argument("--dpi", type=int, metavar="DPI",
                        help="Write a raster image (png, or tiff for a .tif/"
                             ".tiff output name) at this resolution instead of "
                             "an svg. Needs cairosvg, and pillow for tiff.")
    args = parser.parse_args(argv)

    if args.columns < 1:
        parser.error("--columns must be at least 1")
    if args.legend_font_size is not None and args.legend_font_size < 5:
        parser.error("--legend-font-size must be at least 5")
    if args.dpi is not None and args.dpi < 1:
        parser.error("--dpi must be at least 1")
    page_size = None if args.page_size == 'fit' else args.page_size
    try:
        titles = parse_title_overrides(args.titles)
    except ValueError as error:
        parser.error(str(error))
    for path in args.proviral_landscape_csvs:
        if not os.path.exists(path):
            parser.error("input csv file not found: " + path)

    if len(args.proviral_landscape_csvs) == 1:
        # a single input still gets the single-plot layout with its own legend
        lines = read_landscape_csv(args.proviral_landscape_csvs[0])
        create_proviral_plot(lines, args.output_svg, dpi=args.dpi)
    else:
        create_proviral_page(args.proviral_landscape_csvs, args.output_svg,
                             columns=args.columns,
                             title_column=args.title_column,
                             titles=titles,
                             legend_font_size=args.legend_font_size,
                             page_size=page_size,
                             dpi=args.dpi)


if __name__ == '__main__':
    main()
