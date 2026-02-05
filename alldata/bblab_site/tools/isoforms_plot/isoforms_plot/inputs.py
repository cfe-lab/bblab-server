
#
# This file is responsible for parsing of:
#  - splicing sites
#  - transcripts
#  - groups
#  - title
#

END_POS = 9632

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

TITLE = "My plot A"

