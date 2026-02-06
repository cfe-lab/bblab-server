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
import multicsv


class InvalidFragmentError(ValueError):
    def __init__(self, fragment_str: str, previous_str: str, next_str: str) -> None:
        self.fragment_str = fragment_str
        self.previous_str = previous_str
        self.next_str = next_str
        super().__init__(f"Invalid fragment string: '{fragment_str}'. Expected format 'start-end'.")


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


@dataclass(frozen=True)
class Donor:
    name: str
    position: int


@dataclass(frozen=True)
class Acceptor:
    name: str
    position: int


@dataclass(frozen=True)
class AST:
    title: Optional[str]
    transcripts: Sequence[Transcript]
    donors: Sequence[Donor]
    acceptors: Sequence[Acceptor]


def read_transcripts(reader: csv.DictReader) -> Iterator[Transcript]:
    """
    Parse transcripts from CSV rows.

    Expected CSV columns:
    - fragments: Semicolon-separated list of ranges (e.g., "1-743; 4913-end")
    - label: Optional label for the transcript
    - comment: Optional comment
    - group: Optional group name

    Each fragment is "start-end" where:
    - start is an integer
    - end is either an integer or the literal string "end" (mapped to None)
    """
    for row in reader:
        # Parse fragments field
        fragments_str = row.get("fragments", "").strip()
        if not fragments_str:
            continue  # Skip rows with no fragments

        fragments = []
        previous_str = ""
        for fragment_str in fragments_str.split(";"):
            fragment_str = fragment_str.strip()
            if not fragment_str:
                previous_str += fragment_str + ";"
                continue

            # Split on hyphen to get start and end
            parts = fragment_str.split("-", 1)
            if len(parts) != 2:
                next_str = fragments_str[len(previous_str):]
                raise InvalidFragmentError(fragment_str=fragment_str, previous_str=previous_str, next_str=next_str)

            start_str, end_str = parts
            start = int(start_str.strip())

            # Handle "end" keyword (case-insensitive)
            end_str = end_str.strip()
            if end_str.lower() == "end":
                end = None
            else:
                end = int(end_str)

            fragments.append(Fragment(start=start, end=end))
            previous_str += fragment_str + ";"

        # Extract optional fields, converting empty strings to None
        label = (row.get("label") or "").strip() or None
        comment = (row.get("comment") or "").strip() or None
        group = (row.get("group") or "").strip() or None

        yield Transcript(
            fragments=tuple(fragments),
            label=label,
            group=group,
            comment=comment,
        )


def parse_title(rows: Iterator[Sequence[str]]) -> Optional[str]:
    nonempty = [row for row in rows if len(row) > 0]
    if len(nonempty) == 0:
        return None
    if len(nonempty) != 1:
        raise ValueError("Title section must contain exactly one non-empty value.")
    if len(nonempty[0]) != 1:
        raise ValueError("Title section must contain exactly one non-empty value.")

    nonempty_value = nonempty[0][0].strip()
    if not nonempty_value:
        return None
    return nonempty_value


def read_donors(reader: csv.DictReader) -> Iterator[Donor]:
    """
    Parse donors from CSV rows.

    Expected CSV columns:
    - name: Name of the donor site (e.g., "D1", "D2")
    - position: Integer position of the donor site
    """
    for row in reader:
        name = (row.get("name") or "").strip()
        position_str = (row.get("position") or "").strip()

        if not name or not position_str:
            continue  # Skip rows with missing data

        try:
            position = int(position_str)
        except ValueError:
            raise ValueError(
                f"Invalid position '{position_str}' for donor '{name}'. Expected an integer."
            )

        yield Donor(name=name, position=position)


def read_acceptors(reader: csv.DictReader) -> Iterator[Acceptor]:
    """
    Parse acceptors from CSV rows.

    Expected CSV columns:
    - name: Name of the acceptor site (e.g., "A1", "A2")
    - position: Integer position of the acceptor site
    """
    for row in reader:
        name = (row.get("name") or "").strip()
        position_str = (row.get("position") or "").strip()

        if not name or not position_str:
            continue  # Skip rows with missing data

        try:
            position = int(position_str)
        except ValueError:
            raise ValueError(
                f"Invalid position '{position_str}' for acceptor '{name}'. Expected an integer."
            )

        yield Acceptor(name=name, position=position)


def parse(input_file: Path) -> AST:
    with multicsv.open(input_file) as csvfile:
        sections = {section.lower(): section for section in csvfile}

        title_section = csvfile[sections["title"]] if "title" in sections else None
        title = (
            parse_title(csv.reader(title_section))
            if title_section is not None
            else None
        )

        transcripts_section = (
            csvfile[sections["transcripts"]] if "transcripts" in sections else None
        )
        if transcripts_section is None:
            raise ValueError('Input CSV must contain a "Transcripts" section.')

        donors_section = csvfile[sections["donors"]] if "donors" in sections else None
        if donors_section is None:
            raise ValueError('Input CSV must contain a "Donors" section.')

        acceptors_section = (
            csvfile[sections["acceptors"]] if "acceptors" in sections else None
        )
        if acceptors_section is None:
            raise ValueError('Input CSV must contain an "Acceptors" section.')

        reader = csv.DictReader(transcripts_section)
        transcripts = tuple(read_transcripts(reader))

        donors_reader = csv.DictReader(donors_section)
        donors = tuple(read_donors(donors_reader))

        acceptors_reader = csv.DictReader(acceptors_section)
        acceptors = tuple(read_acceptors(acceptors_reader))

    return AST(
        title=title,
        transcripts=transcripts,
        donors=donors,
        acceptors=acceptors,
    )
