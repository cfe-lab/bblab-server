
"""
The job of the compiler is to take parsed inputs and transform them into a form that the plotter can use.
This is where we do things like:
- assign transcripts to groups
- ...
"""

from isoforms_plot.parser import AST

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


def compile(parsed_inputs: AST):
    # for now, we just pass everything through without any changes.
    return {
        'splicing_sites': SPLICING_SITES,
        'transcripts': TRANSCRIPTS,
        'groups': GROUPS,
        'title': parsed_inputs.title,
    }
