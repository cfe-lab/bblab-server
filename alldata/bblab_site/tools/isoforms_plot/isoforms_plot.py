from csv import DictReader
from argparse import ArgumentParser
from genetracks import Figure, Track, Multitrack, Label
from itertools import groupby
from operator import itemgetter
import drawsvg as draw
from collections import defaultdict
from math import ceil


# Multiplier that helps estimating label widths. It is approximate and font-dependent.
CHAR_WIDTH_FACTOR = 0.6


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

# default NL43 landmarks for the small overview graphic
# assigned to three frames (0/1/2) so overlapping genes stack vertically
# tat and rev have multiple exons, so we include both parts
LANDMARKS = [
    {"name": "5'LTR", 'start': 1, 'end': 634, 'colour': '#e0e0e0', 'frame': 0},
    {'name': 'gag', 'start': 790, 'end': 2292, 'colour': '#a6cee3', 'frame': 0},
    {'name': 'pol', 'start': 2085, 'end': 5096, 'colour': '#1f78b4', 'frame': 2},
    {'name': 'vif', 'start': 5041, 'end': 5619, 'colour': '#fb9a99', 'frame': 0},
    {'name': 'vpr', 'start': 5559, 'end': 5849, 'colour': '#fdbf6f', 'frame': 2},
    {'name': 'tat', 'start': 5830, 'end': 6044, 'colour': '#b2df8a', 'frame': 1, 'exon': 1},
    {'name': 'tat', 'start': 8369, 'end': 8414, 'colour': '#b2df8a', 'frame': 0, 'exon': 2},
    {'name': 'rev', 'start': 5970, 'end': 6044, 'colour': '#c2a5cf', 'frame': 2, 'exon': 1},
    {'name': 'rev', 'start': 8369, 'end': 8643, 'colour': '#c2a5cf', 'frame': 1, 'exon': 2},
    {'name': 'vpu', 'start': 6062, 'end': 6306, 'colour': '#ffff99', 'frame': 1},
    {'name': 'env', 'start': 6221, 'end': 8785, 'colour': '#8dd3c7', 'frame': 2},
    {'name': 'nef', 'start': 8787, 'end': 9407, 'colour': '#bebada', 'frame': 0},
    {"name": "3'LTR", 'start': 9086, 'end': 9719, 'colour': '#e0e0e0', 'frame': 1}
]

# default positions of splicing sites in NL43.
SPLICING_SITES = [
    {'name': 'D1', 'start': 743, 'type': 'donor'},
    {'name': 'D2', 'start': 4962, 'type': 'donor'},
    {'name': 'D2b', 'start': 5058, 'type': 'donor'},
    {'name': 'D3', 'start': 5463, 'type': 'donor'},
    {'name': 'D4', 'start': 6046, 'type': 'donor'},
    {'name': 'A1', 'start': 4913, 'type': 'acceptor'},
    {'name': 'A2', 'start': 5390, 'type': 'acceptor'},
    {'name': 'A3', 'start': 5777, 'type': 'acceptor'},
    {'name': 'A4c', 'start': 5936, 'type': 'acceptor'},
    {'name': 'A4a', 'start': 5954, 'type': 'acceptor'},
    {'name': 'A4b', 'start': 5960, 'type': 'acceptor'},
    {'name': 'A5', 'start': 5976, 'type': 'acceptor'},
    {'name': 'A7', 'start': 8369, 'type': 'acceptor'},
]

# Information about individual isoforms to be displayed.
TRANSCRIPTS = [
    {'parts': [(1, 743), (4913, 5463)], 'label': 'vif'},
    {'parts': [(1, 743), (5777, 6046), (8369, 9999)], 'label': 'rev'},
    {'parts': [(1, 743), (5777, 6046), (8369, 9999)], 'label': 'tat'},
    {'parts': [(1, 743), (5777, 6046), (8369, 9999)], 'label': 'rev'},
    {'parts': [(1, 743), (5390, 5463), (5954, 6046), (8369, 9999)], 'label': 'nef'},
    {'parts': [(1, 743), (5954, 6046), (8369, 9999)], 'label': 'nef'},
    {'parts': [(1, 743), (5390, 5463), (5954, 6046), (8369, 9999)], 'label': 'nef'},
    {'parts': [(1, 743), (5777, 6046), (8369, 9999)], 'label': 'tat'},
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
    Draw a simple overview of the reference (NL43) using the provided
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
                    padding = 2
                    avail = w0 - padding
                    while (font * CHAR_WIDTH_FACTOR * len(label)) > avail:
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


class SplicingSites:
    """
    Draw a horizontal line with vertical ticks at splicing site positions.
    Donor sites have ticks going up, acceptor sites have ticks going down.
    Dotted lines extend down from each site through the defects section.
    """
    def __init__(self, splicing_sites, total_samples=0, lineheight=5, h=60):
        self.splicing_sites = splicing_sites
        self.a = START_POS + XOFFSET
        self.b = END_POS + XOFFSET
        self.w = self.b - self.a
        self.h = h  # height of the component (increased for multi-level labels)
        self.line_thickness = 2
        self.tick_height = 10
        self.color = 'black'
        self.font_size = 10
        self.label_spacing = 12  # vertical spacing between label levels
        self.total_samples = total_samples
        self.lineheight = lineheight
        self.dotted_line_thickness = 1  # thin dotted lines

    def _assign_label_levels(self, sites_data, xscale):
        """
        Assign vertical levels to labels to avoid overlaps.
        Returns a dict mapping site index to level (0, 1, 2, ...).
        """
        # Estimate character width for monospace font (rough approximation)
        char_width = self.font_size * CHAR_WIDTH_FACTOR
        min_spacing = 2  # minimum pixels between labels

        # Build list of (index, x_pos, label_width, site_type)
        label_info = []
        for i, site_data in enumerate(sites_data):
            site, x_pos = site_data
            site_name = site.get('name', '')
            label_width = len(site_name) * char_width
            site_type = site.get('type', 'donor')
            label_info.append((i, x_pos, label_width, site_type))

        # Sort by x position
        label_info.sort(key=lambda x: x[1])

        # Separate donors and acceptors (they can overlap since they're on opposite sides)
        donors = [x for x in label_info if x[3] == 'donor']
        acceptors = [x for x in label_info if x[3] == 'acceptor']

        levels = {}

        # Assign levels for each group separately
        for group in [donors, acceptors]:
            if not group:
                continue

            # Greedy algorithm: assign each label to the lowest level where it fits
            level_rightmost = {}  # tracks the rightmost x position at each level

            for idx, x_pos, label_width, site_type in group:
                label_left = x_pos - label_width / 2
                label_right = x_pos + label_width / 2

                # Find the lowest level where this label fits
                level = 0
                while True:
                    if level not in level_rightmost:
                        # This level is empty, use it
                        level_rightmost[level] = label_right + min_spacing
                        levels[idx] = level
                        break
                    elif label_left >= level_rightmost[level]:
                        # This label fits at this level
                        level_rightmost[level] = label_right + min_spacing
                        levels[idx] = level
                        break
                    else:
                        # Try next level
                        level += 1

        return levels

    def draw(self, x=0, y=0, xscale=1.0):
        a = self.a * xscale
        b = self.b * xscale
        x = x * xscale

        d = draw.Group(transform="translate({} {})".format(x, y))

        # Draw horizontal line (baseline for ticks)
        line_y = self.h / 2
        d.append(draw.Lines(a, line_y, b, line_y,
                          stroke=self.color, stroke_width=self.line_thickness))

        # Calculate how far down the dotted lines should extend
        # They should go through all the sample tracks
        dotted_line_length = self.total_samples * (self.lineheight + 1) + 100  # extra padding

        # Collect sites data for label positioning
        sites_data = []
        for site in self.splicing_sites:
            site_pos = site['start']
            # Skip sites outside our display range
            if site_pos < START_POS or site_pos > END_POS:
                continue
            x_pos = (site_pos + XOFFSET) * xscale
            sites_data.append((site, x_pos))

        # Assign levels to avoid overlaps
        levels = self._assign_label_levels(sites_data, xscale)

        # Draw dotted vertical lines extending down from baseline for each site
        for site, x_pos in sites_data:
            dotted_start_y = line_y
            dotted_end_y = line_y - dotted_line_length
            # Create a dotted line using stroke-dasharray
            d.append(draw.Line(x_pos, dotted_start_y, x_pos, dotted_end_y,
                             stroke='lightgray', stroke_width=self.dotted_line_thickness,
                             stroke_dasharray='2,3'))  # 2 pixels dash, 3 pixels gap

        # Draw ticks and labels
        for i, (site, x_pos) in enumerate(sites_data):
            site_type = site.get('type', 'donor')
            site_name = site.get('name', '')
            level = levels.get(i, 0)

            # Donor sites: ticks go up; Acceptor sites: ticks go down
            if site_type == 'donor':
                tick_start = line_y
                tick_end = line_y + self.tick_height
                # Labels above: higher levels go further up
                label_y = tick_end + self.font_size - 5 + (level * self.label_spacing)
            else:  # acceptor
                tick_start = line_y
                tick_end = line_y - self.tick_height
                # Labels below: higher levels go further down
                label_y = tick_end - 5 - (level * self.label_spacing)

            # Draw tick
            d.append(draw.Lines(x_pos, tick_start, x_pos, tick_end,
                              stroke=self.color, stroke_width=self.line_thickness))

            # Draw label
            d.append(draw.Text(text=site_name, font_size=self.font_size,
                             x=x_pos, y=label_y,
                             font_family='monospace', center=True, fill=self.color))

        return d


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
    def __init__(self, defect_percentages, highlighted, total_samples, lineheight, xaxisheight, force_move_percentages=False):
        self.a = START_POS + XOFFSET
        self.b = END_POS + XOFFSET
        self.w = self.b - self.a
        self.defect_types = defect_percentages.keys()
        self.highlighted_types = highlighted
        self.defect_percentages = defect_percentages
        self.num_samples = total_samples
        # number of legend lines (3 columns)
        self.num_lines = (len(self.defect_types) + len(self.highlighted_types)) / 3
        self.h = 20 * self.num_lines
        self.lineheight = lineheight
        self.xaxisheight = xaxisheight
        # if True, move percentages into legend (used when any category is small)
        self.force_move_percentages = force_move_percentages

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
        fontsize = 20

        # Determine whether to move percentages into the legend
        # move_percentages_to_legend is controlled externally via force_move_percentages flag
        move_percentages_to_legend = bool(self.force_move_percentages)

        d = draw.Group(transform="translate({} {})".format(x, y))

        d.append(Label(-10, "Seq.", font_size=20, offset=yaxis_label_height + 12).draw(x=(a - 30)))
        d.append(Label(-10, f"N={self.num_samples}", font_size=20, offset=yaxis_label_height - 12).draw(x=(a - 30)))

        # draw legend; optionally include percentages in the legend labels
        self.add_legend(a, column_space, barlen, barheight, d, include_percentages=move_percentages_to_legend)

        # only draw the sidebar when percentages are not moved into the legend
        if not move_percentages_to_legend:
            self.add_sidebar(sidebar_x, sidebar_ystart, fontsize, d)

        return d


class IsoformsPlot:
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

    def legends_and_percentages(self, defect_percentages, highlight_types, force_move_percentages=False):
        self.figure.add(LegendAndPercentages(defect_percentages,
                                             highlight_types,
                                             self.tot_samples,
                                             self.lineheight,
                                             self.xaxisheight,
                                             force_move_percentages))


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


def create_isoforms_plot(input_file, output_svg):
    # Use TRANSCRIPTS to determine number of samples to display
    total_samples = len(TRANSCRIPTS)
    figure = Figure()
    plot = IsoformsPlot(figure, total_samples)
    # add genome overview at the top of the figure so it appears above sample tracks
    add_genome_overview(figure, LANDMARKS)
    # add splicing sites display below the genome overview
    figure.add(SplicingSites(SPLICING_SITES, total_samples=total_samples, lineheight=plot.lineheight), gap=5)
    # add a small blank multitrack to create vertical separation between the splicing sites
    # and the sample tracks (gap value tuned to avoid overlap with multi-level labels)
    try:
        figure.add(Multitrack([Track(START_POS + XOFFSET, START_POS + XOFFSET, color='#ffffff', h=2)]), gap=25)
    except TypeError:
        # fallback if Track signature differs; attempt without named color
        figure.add(Multitrack([Track(START_POS + XOFFSET, START_POS + XOFFSET, color='#ffffff', h=2)]), gap=25)

    # Draw each transcript from TRANSCRIPTS variable
    default_color = 'grey'
    for i, transcript in enumerate(TRANSCRIPTS):
        transcript_name = f"transcript_{i}"
        color = transcript.get('color', default_color)
        parts = transcript.get('parts', [])

        # Draw each part of the transcript
        for part in parts:
            if len(part) == 2:
                xstart, xend = part
                # Create a multitrack with a single track for this part
                track = Track(xstart + XOFFSET, xend + XOFFSET, color=color, h=plot.lineheight)
                plot.curr_multitrack.append(track)

        # Finish this transcript line
        plot.draw_current_multitrack()

    # finalize plot
    plot.add_xaxis()
    # display with a standard width so the overview is visible
    figure.show(w=900).save_svg(output_svg)


def main():
    parser = ArgumentParser()
    parser.add_argument("output_svg",
                        help="Output SVG")
    args = parser.parse_args()

    create_isoforms_plot(None, args.output_svg)


if __name__ == '__main__':
    main()
