
#
# This file is responsible for parsing of:
#  - splicing sites
#  - transcripts
#  - groups
#  - title
#

import csv
from pathlib import Path


def parse(input_file: Path) -> dict:
    with input_file.open() as fd:
        reader = csv.DictReader(fd)
        assert reader.fieldnames is not None
        transcripts: list = []

    return {
        'transcripts': transcripts,
    }

