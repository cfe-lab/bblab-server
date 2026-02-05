from argparse import ArgumentParser
from genetracks import Figure, Track, Multitrack, Label
from operator import itemgetter
import drawsvg as draw
from collections import defaultdict


# Multiplier that helps estimating label widths. It is approximate and font-dependent.
CHAR_WIDTH_FACTOR = 0.6

DOTTED_LINES_WIDTH = 1

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
    {'parts': [(1, 743), (4913, END_POS)], 'label': 'vif'},
    {'parts': [(1, 743), (5777, 6046), (5954, END_POS)], 'label': 'vpu/env'},
    {'parts': [(1, 743), (5390, 5463), (5954, END_POS)]},
    {'parts': [(1, 743), (4913, 4962), (5390, 5463), (5954, END_POS)]},
    {'parts': [(1, 743), (5390, 5463), (5954, END_POS)]},
    {'parts': [(1, 743), (5777, 6046), (8369, END_POS)], 'label': 'rev', 'comment': '(interesting, eh?!)'},
    {'parts': [(1, 743), (5777, 6046), (8369, END_POS)], 'comment': '(3 copies)'},
    {'parts': [(1, 743), (5777, 6046), (8369, END_POS)], 'label': 'tat'},
    {'parts': [(1, 743), (5777, 6046), (8369, END_POS)]},
    {'parts': [(1, 743), (5390, 5463), (5954, 6046), (8369, END_POS)], 'label': 'nef', 'comment': '(two like this)'},
    {'parts': [(1, 743), (5954, 6046), (8369, END_POS)]},
    {'parts': [(1, 743), (5390, 5463), (5954, 6046), (8369, END_POS)]},
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


class SplicingSites:
    """
    Draw a horizontal line with vertical ticks at splicing site positions.
    Donor sites have ticks going up, acceptor sites have ticks going down.
    Dotted lines extend down from each site through the transcripts section.
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
        self.dotted_line_thickness = DOTTED_LINES_WIDTH

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
            # Create a dotted line using round dots
            # Use stroke-linecap='round' with stroke-dasharray to get round dots
            d.append(draw.Line(x_pos, dotted_start_y, x_pos, dotted_end_y,
                             stroke='lightgray', stroke_width=1.5,
                             stroke_dasharray='0.3,3',
                             stroke_linecap='round'))  # makes ends round

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


class TranscriptLine:
    """Draws a transcript with its parts and optional label on the right side."""
    def __init__(self, parts, color, label=None, comment=None, lineheight=5):
        self.parts = parts
        self.color = color
        self.label = label
        self.comment = comment
        self.lineheight = lineheight
        self.font_size = 9  # smaller font
        self.comment_font_size = 8  # slightly smaller for comments
        # If there's a label, increase height to accommodate it
        if self.label:
            # Need enough total height to avoid overlap with previous transcript
            # But position label close to own transcript
            self.h = self.lineheight + self.font_size + 6  # increased total height
        else:
            self.h = self.lineheight
        self.a = START_POS + XOFFSET
        self.b = END_POS + XOFFSET
        # Calculate width in logical coordinates (like XAxis does)
        if self.comment:
            # Estimate comment width in pixels
            comment_width = len(self.comment) * self.comment_font_size * 0.6
            # Estimated xscale: target display width / logical genome width
            # Assuming display ~900px and genome is END_POS + XOFFSET ≈ 10032
            estimated_xscale = 900.0 / (END_POS + XOFFSET)
            # Convert comment pixel width to logical units
            comment_logical_width = comment_width / estimated_xscale
            # Width in logical coords: genome end + gap + comment + padding
            self.w = END_POS + XOFFSET + 100 + comment_logical_width
        else:
            self.w = END_POS + XOFFSET + 1500  # match XAxis default

    def draw(self, x=0, y=0, xscale=1.0):
        d = draw.Group(transform="translate({} {})".format(x * xscale, y))

        # Transcript at top
        transcript_y = 0

        if self.label:
            # Label baseline very close to transcript - minimal gap
            label_baseline_y = self.lineheight + int(self.font_size * 0.5)
        else:
            label_baseline_y = None

        # Draw transcript rectangles
        for part in self.parts:
            if len(part) == 2:
                xstart, xend = part
                xstart_scaled = (xstart + XOFFSET) * xscale + DOTTED_LINES_WIDTH
                xend_scaled = (xend + XOFFSET) * xscale - DOTTED_LINES_WIDTH
                width = xend_scaled - xstart_scaled
                d.append(draw.Rectangle(xstart_scaled, transcript_y, width, self.lineheight,
                                       fill=self.color, stroke=self.color))

        # Draw label text
        if self.label and label_baseline_y is not None:
            # Right-align labels at END_POS
            label_x = (END_POS + XOFFSET) * xscale
            d.append(draw.Text(text=self.label, font_size=self.font_size,
                             x=label_x, y=label_baseline_y,
                             font_family='monospace', fill='black',
                             text_anchor='end'))  # right-align text

        # Draw comment text (to the right of transcript, at same height)
        if self.comment:
            # Position in logical coordinates: genome end + small gap (in logical units)
            # This will be scaled by xscale along with everything else
            comment_x = (END_POS + XOFFSET + 20) * xscale
            # Use middle of transcript for y, and set dominant-baseline to middle for proper centering
            comment_y = transcript_y + self.lineheight / 2
            d.append(draw.Text(text=self.comment, font_size=self.comment_font_size,
                             x=comment_x, y=comment_y,
                             font_family='monospace', fill='gray',
                             text_anchor='start',  # left-align comment
                             dominant_baseline='middle'))  # vertically center text

        return d


def create_isoforms_plot(input_file, output_svg):
    # Use TRANSCRIPTS to determine number of samples to display
    total_samples = len(TRANSCRIPTS)
    figure = Figure()
    lineheight = 500 / total_samples if total_samples > 0 else 0
    if lineheight > 5:
        lineheight = 5
    # add genome overview at the top of the figure so it appears above sample tracks
    add_genome_overview(figure, LANDMARKS)
    # add splicing sites display below the genome overview
    figure.add(SplicingSites(SPLICING_SITES, total_samples=total_samples, lineheight=lineheight), gap=5)
    # add a small blank multitrack to create vertical separation between the splicing sites
    # and the sample tracks (gap value tuned to avoid overlap with multi-level labels)
    try:
        figure.add(Multitrack([Track(START_POS + XOFFSET, START_POS + XOFFSET, color='#ffffff', h=2)]), gap=25)
    except TypeError:
        # fallback if Track signature differs; attempt without named color
        figure.add(Multitrack([Track(START_POS + XOFFSET, START_POS + XOFFSET, color='#ffffff', h=2)]), gap=25)

    # Draw each transcript from TRANSCRIPTS variable
    default_color = 'grey'
    max_comment_width = 0
    comment_font_size = 8
    for i, transcript in enumerate(TRANSCRIPTS):
        color = transcript.get('color', default_color)
        parts = transcript.get('parts', [])
        label = transcript.get('label', None)
        comment = transcript.get('comment', None)
        
        # Track maximum comment width
        if comment:
            comment_width = len(comment) * comment_font_size * 0.6
            max_comment_width = max(max_comment_width, comment_width)

        # Create and add transcript line with label and comment
        transcript_line = TranscriptLine(parts, color, label, comment, lineheight=lineheight)
        figure.add(transcript_line, gap=3)  # gap between transcripts

    # Calculate figure width to accommodate comments
    # Use reasonable display width so genome fits on screen (900px)
    # Add extra width for comment text (which doesn't scale with xscale)
    figure_width = 900 + int(max_comment_width) + 100
    # display with width that includes comments
    figure.show(w=figure_width).save_svg(output_svg)


def main():
    parser = ArgumentParser()
    parser.add_argument("output_svg",
                        help="Output SVG")
    args = parser.parse_args()

    create_isoforms_plot(None, args.output_svg)


if __name__ == '__main__':
    main()
