"""
This file is responsible for parsing of:
  - splicing sites
  - transcripts
  - groups
  - title
"""

import csv
import re
from dataclasses import dataclass
from typing import Iterator, Literal, Optional, Sequence, TypeAlias
import multicsv
from . import exceptions as ex


SpliceSiteColour: TypeAlias = Literal[
    "red",
    "blue",
    "green",
    "orange",
    "purple",
    "cyan",
    "magenta",
    "yellow",
    "pink",
    "brown",
    "lime",
    "navy",
]


# Regex for trailing colour annotation: <range>...(...)
COLOUR_ANNOTATION_RE = re.compile(r"(?P<range>.+?)\s*\((?P<colour>[^()]*)\)\s*\Z")

# Predefined list of allowed splice site colours
ALLOWED_COLOURS: tuple[SpliceSiteColour, ...] = (
    "red",
    "blue",
    "green",
    "orange",
    "purple",
    "cyan",
    "magenta",
    "yellow",
    "pink",
    "brown",
    "lime",
    "navy",
)


@dataclass(frozen=True)
class Fragment:
    start: int
    end: Optional[int]
    colour: Optional[SpliceSiteColour] = None


@dataclass(frozen=True)
class Transcript:
    fragments: Sequence[Fragment]
    label: Optional[str]
    group: Optional[str]
    N_observed: Optional[str]


@dataclass(frozen=True)
class Donor:
    name: str
    position: int
    colour: Optional[SpliceSiteColour]


@dataclass(frozen=True)
class Acceptor:
    name: str
    position: int
    colour: Optional[SpliceSiteColour]


@dataclass(frozen=True)
class AST:
    title: Optional[str]
    transcripts: Sequence[Transcript]
    donors: Sequence[Donor]
    acceptors: Sequence[Acceptor]


def parse_fragment(
    raw_fragment: str,
    previous_str: str,
    next_str: str,
) -> Fragment:
    """
    Parse a single fragment string (e.g. ``"5390-5463"`` or ``"5390-5463 (red)"``)
    into a ``Fragment``.

    Raises the usual parse errors for malformed ranges, and additionally
    ``InvalidFragmentColourSyntaxError`` / ``EmptyFragmentColourError`` /
    ``InvalidFragmentColourError`` for malformed colour annotations.
    """
    fragment_str = raw_fragment.strip()

    if not fragment_str:
        raise ex.EmptyFragmentError(
            fragment_str=raw_fragment,
            previous_str=previous_str,
            next_str=next_str,
        )

    colour = None
    range_str = fragment_str

    # If the fragment contains parentheses, require a valid trailing colour annotation
    if "(" in fragment_str or ")" in fragment_str:
        match = COLOUR_ANNOTATION_RE.match(fragment_str)
        if not match:
            raise ex.InvalidFragmentColourSyntaxError(
                fragment_str=raw_fragment,
                previous_str=previous_str,
                next_str=next_str,
            )

        range_str = match.group("range").strip()
        colour_raw = match.group("colour").strip()

        # Range part must not contain parentheses
        if "(" in range_str or ")" in range_str:
            raise ex.InvalidFragmentColourSyntaxError(
                fragment_str=raw_fragment,
                previous_str=previous_str,
                next_str=next_str,
            )

        # Range must not end with a bare dash (colour used as end coordinate)
        if range_str.endswith("-"):
            raise ex.InvalidFragmentColourSyntaxError(
                fragment_str=raw_fragment,
                previous_str=previous_str,
                next_str=next_str,
            )

        if not colour_raw:
            raise ex.EmptyFragmentColourError(
                fragment_str=raw_fragment,
                previous_str=previous_str,
                next_str=next_str,
            )

        if colour_raw not in ALLOWED_COLOURS:
            raise ex.InvalidFragmentColourError(
                fragment_str=raw_fragment,
                colour=colour_raw,
                allowed_colours=ALLOWED_COLOURS,
                previous_str=previous_str,
                next_str=next_str,
            )

        colour = colour_raw

    # Validate range shape before parsing integers
    dash_count = range_str.count("-")
    if dash_count == 0:
        raise ex.InvalidDashPatternError(
            fragment_str=raw_fragment,
            previous_str=previous_str,
            next_str=next_str,
        )
    if dash_count > 1:
        raise ex.TooManyDashesInFragmentError(
            fragment_str=raw_fragment,
            previous_str=previous_str,
            next_str=next_str,
        )

    # Exactly one dash: split into start and end
    start_str, end_str = range_str.split("-", 1)
    start_str = start_str.strip()
    try:
        start = int(start_str)
    except BaseException:
        raise ex.NotIntegerStartError(
            start_str=start_str,
            fragment_str=raw_fragment,
            previous_str=previous_str,
            next_str=next_str,
        )

    if start < 1:
        raise ex.NotPositiveStartError(
            start=start,
            fragment_str=raw_fragment,
            previous_str=previous_str,
            next_str=next_str,
        )

    end_str = end_str.strip()
    if end_str.lower() == "end":
        end = None
    else:
        try:
            end = int(end_str)
        except BaseException:
            raise ex.NotIntegerEndError(
                end_str=end_str,
                fragment_str=raw_fragment,
                previous_str=previous_str,
                next_str=next_str,
            )
        if end < 1:
            raise ex.NotPositiveEndError(
                end=end,
                fragment_str=raw_fragment,
                previous_str=previous_str,
                next_str=next_str,
            )
        if end < start:
            raise ex.EndLessThanStartError(
                start=start,
                end=end,
                fragment_str=raw_fragment,
                previous_str=previous_str,
                next_str=next_str,
            )

    return Fragment(start=start, end=end, colour=colour)


def read_transcripts(reader: csv.DictReader) -> Iterator[Transcript]:
    """
    Parse transcripts from CSV rows.

    Expected CSV columns:
    - fragments: Semicolon-separated list of ranges (e.g., "1-743; 4913-end")
    - label: Optional label for the transcript
    - N_observed: Optional number of observations
    - group: Optional group name

    Each fragment is "start-end" where:
    - start is an integer
    - end is either an integer or the literal string "end" (mapped to None)
    """
    for row in reader:
        # Skip completely empty rows (all fields are empty or whitespace)
        if not row or all(not str(v).strip() for v in row.values()):
            continue

        # Parse fragments field
        fragments_str = row.get("fragments", "").strip()
        if not fragments_str:
            raise ex.MissingFragmentsError(row=row)

        fragments = []
        split_fragments = fragments_str.split(";")

        for j, raw_fragment in enumerate(split_fragments):
            # Build context for error messages
            parts_before = ";".join(split_fragments[:j])
            parts_after = ";".join(split_fragments[j + 1:])
            previous_str = parts_before + ";" if parts_before else ""
            next_str = ";" + parts_after if parts_after else ""

            fragment = parse_fragment(raw_fragment, previous_str, next_str)
            fragments.append(fragment)

        # Extract optional fields, converting empty strings to None
        label = (row.get("label") or "").strip() or None
        N_observed = (row.get("N_observed") or "").strip() or None
        group = (row.get("group") or "").strip() or None

        yield Transcript(
            fragments=tuple(fragments),
            label=label,
            group=group,
            N_observed=N_observed,
        )


def parse_title(rows: Iterator[Sequence[str]]) -> Optional[str]:
    nonempty_values = [value.strip() for row in rows for value in row if value.strip()]
    if len(nonempty_values) == 0:
        return None
    if len(nonempty_values) > 1:
        raise ex.TitleSectionTooManyNonEmptyValuesError(nonempty=nonempty_values)

    nonempty_value = nonempty_values[0]
    return nonempty_value


def read_donors(reader: csv.DictReader) -> Iterator[Donor]:
    """
    Parse donors from CSV rows.

    Expected CSV columns:
    - name: Name of the donor site (e.g., "D1", "D2")
    - position: Integer position of the donor site
    - colour: Optional colour (e.g., "red", "blue"). Must not be grey, black, or white.
    """
    for row in reader:
        # Skip completely empty rows (all fields are empty or whitespace)
        if not row or all(not str(v).strip() for v in row.values()):
            continue

        name = (row.get("name") or "").strip()
        position_str = (row.get("position") or "").strip()
        colour = (row.get("colour") or "").strip() or None

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

        # Validate colour if provided
        if colour:
            if colour not in ALLOWED_COLOURS:
                raise ex.InvalidSpliceSiteColourError(
                    site_type="donor",
                    site_name=name,
                    colour=colour,
                    allowed_colours=ALLOWED_COLOURS,
                    row=row,
                )

        yield Donor(name=name, position=position, colour=colour)


def read_acceptors(reader: csv.DictReader) -> Iterator[Acceptor]:
    """
    Parse acceptors from CSV rows.

    Expected CSV columns:
    - name: Name of the acceptor site (e.g., "A1", "A2")
    - position: Integer position of the acceptor site
    - colour: Optional colour (e.g., "red", "blue"). Must not be grey, black, or white.
    """
    for row in reader:
        # Skip completely empty rows (all fields are empty or whitespace)
        if not row or all(not str(v).strip() for v in row.values()):
            continue

        name = (row.get("name") or "").strip()
        position_str = (row.get("position") or "").strip()
        colour = (row.get("colour") or "").strip() or None

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

        # Validate colour if provided
        if colour:
            if colour not in ALLOWED_COLOURS:
                raise ex.InvalidSpliceSiteColourError(
                    site_type="acceptor",
                    site_name=name,
                    colour=colour,
                    allowed_colours=ALLOWED_COLOURS,
                    row=row,
                )

        yield Acceptor(name=name, position=position, colour=colour)


def parse(csvfile: multicsv.MultiCSVFile) -> AST:
    multisections = {
        section.lower(): [
            other for other in csvfile if other.lower() == section.lower()
        ]
        for section in csvfile
    }
    if any(len(matches) > 1 for matches in multisections.values()):
        raise ex.MultipleSectionsWithSameNameError(multisections=multisections)

    sections = {name.lower(): value for name, value in csvfile.items()}

    title_section = sections.get("title")
    title = (
        parse_title(csv.reader(title_section)) if title_section is not None else None
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
