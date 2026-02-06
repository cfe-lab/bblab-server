"""
This file is responsible for parsing of:
  - splicing sites
  - transcripts
  - groups
  - title
"""

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional, Sequence
import multicsv
from itertools import accumulate
import isoforms_plot.exceptions as ex


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
            raise ex.MissingFragmentsError(row=row)

        fragments = []
        previous_str = ""
        split_fragments = fragments_str.split(";")
        accumulated_splits = accumulate(
            split_fragments, lambda acc, this_fragment: ";".join([acc, this_fragment])
        )

        for fragment_str, previous_str in zip(split_fragments, accumulated_splits):
            next_str = fragments_str[len(previous_str) :]

            fragment_str = fragment_str.strip()
            if not fragment_str:
                raise ex.EmptyFragmentError(
                    fragment_str=fragment_str,
                    previous_str=previous_str,
                    next_str=next_str,
                )

            # Split on hyphen to get start and end
            parts = fragment_str.split("-", 1)
            if len(parts) != 2:
                raise ex.InvalidDashPatternError(
                    fragment_str=fragment_str,
                    previous_str=previous_str,
                    next_str=next_str,
                )

            start_str, end_str = parts
            start_str = start_str.strip()
            try:
                start = int(start_str)
            except BaseException:
                raise ex.NotIntegerStartError(
                    start_str=start_str,
                    fragment_str=fragment_str,
                    previous_str=previous_str,
                    next_str=next_str,
                )

            if start < 1:
                raise ex.NotPositiveStartError(
                    start=start,
                    fragment_str=fragment_str,
                    previous_str=previous_str,
                    next_str=next_str,
                )

            # Handle "end" keyword (case-insensitive)
            end_str = end_str.strip()
            if end_str.lower() == "end":
                end = None
            else:
                try:
                    end = int(end_str)
                except BaseException:
                    raise ex.NotIntegerEndError(
                        end_str=end_str,
                        fragment_str=fragment_str,
                        previous_str=previous_str,
                        next_str=next_str,
                    )
                if end < 1:
                    raise ex.NotPositiveEndError(
                        end=end,
                        fragment_str=fragment_str,
                        previous_str=previous_str,
                        next_str=next_str,
                    )
                if end < start:
                    raise ex.EndLessThanStartError(
                        start=start,
                        end=end,
                        fragment_str=fragment_str,
                        previous_str=previous_str,
                        next_str=next_str,
                    )

            fragments.append(Fragment(start=start, end=end))

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
    if len(nonempty) > 1:
        raise ex.TitleSectionTooManyNonEmptyValuesError(nonempty=nonempty)
    if len(nonempty[0]) != 1:
        raise ex.TitleSectionTooManyColumnsError(row=nonempty[0])

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
        if not row:
            continue  # Skip empty rows

        name = (row.get("name") or "").strip()
        position_str = (row.get("position") or "").strip()

        if not name:
            raise ex.MissingDonorNameError(row=row)
        if not position_str:
            raise ex.MissingDonorPositionError(donor_name=name, row=row)

        try:
            position = int(position_str)
        except ValueError:
            raise ex.InvalidDonorPositionError(
                position_str=position_str, donor_name=name, row=row
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
        if not row:
            continue  # Skip empty rows

        name = (row.get("name") or "").strip()
        position_str = (row.get("position") or "").strip()

        if not name:
            raise ex.MissingAcceptorNameError(row=row)
        if not position_str:
            raise ex.MissingAcceptorPositionError(acceptor_name=name, row=row)

        try:
            position = int(position_str)
        except ValueError:
            raise ex.InvalidAcceptorPositionError(
                position_str=position_str, acceptor_name=name, row=row
            )

        yield Acceptor(name=name, position=position)


def parse(input_file: Path) -> AST:
    with multicsv.open(input_file) as csvfile:
        multisections = {
            section.lower(): [
                other for other in csvfile[section] if other.lower() == section.lower()
            ]
            for section in csvfile
        }
        if any(len(matches) > 1 for matches in multisections.values()):
            raise ex.MultipleSectionsWithSameNameError(multisections=multisections)

        sections = {name.lower(): value for name, value in csvfile.items()}

        title_section = sections.get("title")
        title = (
            parse_title(csv.reader(title_section))
            if title_section is not None
            else None
        )

        transcripts_section = sections.get("transcripts")
        if transcripts_section is None:
            raise ex.MissingTranscriptsSectionError(sections=sections)

        donors_section = sections.get("donors")
        if donors_section is None:
            raise ex.MissingDonorsSectionError(sections=sections)

        acceptors_section = sections.get("acceptors")
        if acceptors_section is None:
            raise ex.MissingAcceptorsSectionError(sections=sections)

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
