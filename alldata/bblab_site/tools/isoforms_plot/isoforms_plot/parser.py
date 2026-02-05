
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

