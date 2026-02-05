
#
# This file is responsible for parsing of:
#  - splicing sites
#  - transcripts
#  - groups
#  - title
#

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional, Sequence


@dataclass(frozen=True)
class Fragment:
    start: int
    end: Optional[int]


@dataclass(frozen=True)
class Transcript:
    fragments: Sequence[Fragment]
    label: Optional[str]
    group: Optional[str]
    comment: Optional[str]


def read_transcripts(reader: csv.DictReader) -> Iterator[Transcript]:
    raise NotImplementedError("Parsing from CSV is not implemented yet.")


def parse(input_file: Path) -> dict:
    with input_file.open() as fd:
        reader = csv.DictReader(fd)
        transcripts = tuple(read_transcripts(reader))

    return {
        'transcripts': transcripts,
    }
