
#
# This file is responsible for parsing of:
#  - splicing sites
#  - transcripts
#  - groups
#  - title
#

import csv
from pathlib import Path
from typing import Optional, TextIO
import multicsv


END_POS = 9632

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

# Information about groups.
GROUPS = [
    {'name': 'My Group 1', 'size': 3},
    {'name': None, 'size': 7},
    {'name': 'My Last Group', 'size': 2},
]


def parse_title(title_section: TextIO) -> Optional[str]:
    reader = csv.reader(title_section)
    rows = list(reader)
    if not rows:
        raise ValueError("Title section is empty.")

    nonempty = [row for row in rows if len(row) > 0]
    if len(nonempty) != 1:
        raise ValueError("Title section must contain exactly one non-empty value.")
    if len(nonempty[0]) != 1:
        raise ValueError("Title section must contain exactly one non-empty value.")

    nonempty_value = nonempty[0][0].strip()
    if not nonempty_value:
        return None
    return nonempty_value


def parse(input_file: Path) -> dict:

    with multicsv.open(input_file) as csv_file:
        title_section = csv_file.get("title", None)
        if title_section is None:
            title = None
        else:
            title = parse_title(title_section)

    return {
        "title": title,
    }

