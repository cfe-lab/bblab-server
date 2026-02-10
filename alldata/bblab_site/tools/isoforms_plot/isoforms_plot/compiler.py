"""
The job of the compiler is to take parsed inputs and transform them into a form that the plotter can use.
This is where we do things like:
- assign transcripts to groups
- convert Fragment objects to tuples
- resolve "end" (None) to END_POS
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Literal, Optional, Sequence, Tuple

from isoforms_plot.parser import AST, Transcript, SpliceSiteColour
import isoforms_plot.exceptions as ex

END_POS = 9632


@dataclass(frozen=True)
class CompiledSplicingSite:
    name: str
    start: int
    type: Literal["donor", "acceptor"]
    colour: Optional[SpliceSiteColour]


@dataclass(frozen=True)
class CompiledFragment:
    start: int
    end: int
    colour: Optional[SpliceSiteColour]


@dataclass(frozen=True)
class CompiledTranscript:
    parts: Sequence[CompiledFragment]
    label: Optional[str]
    comment: Optional[str]


@dataclass(frozen=True)
class CompiledGroup:
    name: Optional[str]
    size: int


@dataclass(frozen=True)
class Compiled:
    transcripts: Sequence[CompiledTranscript]
    groups: Sequence[CompiledGroup]
    splicing_sites: Sequence[CompiledSplicingSite]
    title: Optional[str]


def compile_transcripts(
    parsed_transcripts: Sequence[Transcript],
    valid_starts: set[int],
    valid_ends: set[int],
    acceptor_colours: dict[int, Optional[str]],
    donor_colours: dict[int, Optional[str]],
) -> Tuple[Sequence[CompiledTranscript], Sequence[CompiledGroup]]:

    # Validate transcripts have fragments
    for i, transcript in enumerate(parsed_transcripts):
        if not transcript.fragments:
            raise ex.EmptyTranscriptError(transcript_index=i)

    # Convert transcripts to plotter format
    compiled_transcripts = []
    for i, transcript in enumerate(parsed_transcripts):
        # Convert fragments to CompiledFragment objects with colours
        compiled_parts = []
        for j, fragment in enumerate(transcript.fragments):
            start = fragment.start
            end = fragment.end if fragment.end is not None else END_POS

            # Determine fragment colour based on splice sites it touches
            start_colour = acceptor_colours.get(start)
            end_colour = donor_colours.get(end)

            # Check for conflicting colours
            if (
                start_colour is not None
                and end_colour is not None
                and start_colour != end_colour
            ):
                raise ex.ConflictingFragmentColoursError(
                    transcript_index=i,
                    fragment_index=j,
                    start_position=start,
                    end_position=end,
                    start_colour=start_colour,
                    end_colour=end_colour,
                )

            # Fragment adopts colour from either end (they match or only one is coloured)
            fragment_colour = start_colour or end_colour

            compiled_parts.append(
                CompiledFragment(start=start, end=end, colour=fragment_colour)
            )

        parts_tuple = tuple(compiled_parts)

        # Validate fragment start/end positions
        for j, part in enumerate(parts_tuple):
            start, end = part.start, part.end
            if start not in valid_starts:
                raise ex.InvalidFragmentStartError(
                    transcript_index=i,
                    fragment_index=j,
                    start_position=start,
                    valid_starts=sorted(valid_starts),
                )
            if end not in valid_ends:
                raise ex.InvalidFragmentEndError(
                    transcript_index=i,
                    fragment_index=j,
                    end_position=end,
                    valid_ends=sorted(valid_ends),
                )

        # Validate fragments don't overlap
        for j in range(len(parts_tuple) - 1):
            current = parts_tuple[j]
            next_part = parts_tuple[j + 1]
            if current.end >= next_part.start:
                raise ex.OverlappingFragmentsError(
                    transcript_index=i,
                    fragment_index=j,
                    current_fragment=(current.start, current.end),
                    next_fragment=(next_part.start, next_part.end),
                )

        compiled_transcripts.append(
            CompiledTranscript(
                parts=parts_tuple,
                label=transcript.label,
                comment=transcript.comment,
            )
        )

    # Deduplicate consecutive labels
    # e.g., gag -> vpr -> vpr -> vpr becomes gag -> vpr -> None -> None
    prev_label = None
    deduplicated_transcripts = []
    for transcript in compiled_transcripts:
        current_label = transcript.label
        if current_label is not None and current_label == prev_label:
            # Remove duplicate consecutive label
            deduplicated_transcripts.append(
                CompiledTranscript(
                    parts=transcript.parts,
                    label=None,
                    comment=transcript.comment,
                )
            )
        else:
            deduplicated_transcripts.append(transcript)
        prev_label = current_label if current_label is not None else prev_label

    compiled_transcripts = deduplicated_transcripts

    # Build groups structure
    # Preserve order of first appearance
    groups_order = []
    group_counts = defaultdict(int)
    SENTINEL = object()  # Unique sentinel that's not None
    last_group = SENTINEL
    last_group_count = 0
    for transcript in parsed_transcripts:
        if transcript.group != last_group:
            if last_group is not SENTINEL:
                group_counts[last_group] = last_group_count
            last_group = transcript.group
            groups_order.append(transcript.group)
            last_group_count = 0
        last_group_count += 1

    group_counts[last_group] = last_group_count  # for the final group

    # Build groups list
    compiled_groups = [
        CompiledGroup(name=group_name, size=group_counts[group_name])
        for group_name in groups_order
    ]

    return compiled_transcripts, compiled_groups


def compile(parsed_inputs: AST) -> Compiled:
    """
    Compile parsed AST into plotter-ready format.

    Transforms:
    - Fragment(start, end) to (start, end) tuple where end=None becomes END_POS
    - Transcript objects to CompiledTranscript dataclasses
    - Groups transcripts by their 'group' attribute into CompiledGroup dataclasses
    - Donor/Acceptor objects to CompiledSplicingSite dataclasses

    Validates:
    - No duplicate donor names
    - No duplicate acceptor names
    - Transcripts have at least one fragment
    - Fragment starts are at position 1 or an acceptor site
    - Fragment ends are at END_POS or a donor site
    - Fragments within transcripts do not overlap
    """

    # Validate donor names are unique
    donor_names = [donor.name for donor in parsed_inputs.donors]
    donor_name_counts = Counter(donor_names)
    for name, count in donor_name_counts.items():
        if count > 1:
            positions = [
                donor.position for donor in parsed_inputs.donors if donor.name == name
            ]
            raise ex.DuplicateDonorNameError(name=name, positions=positions)

    # Validate acceptor names are unique
    acceptor_names = [acceptor.name for acceptor in parsed_inputs.acceptors]
    acceptor_name_counts = Counter(acceptor_names)
    for name, count in acceptor_name_counts.items():
        if count > 1:
            positions = [
                acceptor.position
                for acceptor in parsed_inputs.acceptors
                if acceptor.name == name
            ]
            raise ex.DuplicateAcceptorNameError(name=name, positions=positions)

    # Build sets of valid start and end positions
    valid_starts = {1} | {acceptor.position for acceptor in parsed_inputs.acceptors}
    valid_ends = {END_POS} | {donor.position for donor in parsed_inputs.donors}

    # Build colour mappings for splice sites (position -> colour)
    # Position 1 and END_POS have no associated colour (None)
    acceptor_colours: dict[int, Optional[str]] = {1: None}
    for acceptor in parsed_inputs.acceptors:
        acceptor_colours[acceptor.position] = acceptor.colour

    donor_colours: dict[int, Optional[str]] = {END_POS: None}
    for donor in parsed_inputs.donors:
        donor_colours[donor.position] = donor.colour

    compiled_transcripts, compiled_groups = compile_transcripts(
        parsed_inputs.transcripts,
        valid_starts,
        valid_ends,
        acceptor_colours,
        donor_colours,
    )

    # Convert donors and acceptors to splicing sites
    splicing_sites = []
    for donor in parsed_inputs.donors:
        splicing_sites.append(
            CompiledSplicingSite(
                name=donor.name,
                start=donor.position,
                type="donor",
                colour=donor.colour,
            )
        )
    for acceptor in parsed_inputs.acceptors:
        splicing_sites.append(
            CompiledSplicingSite(
                name=acceptor.name,
                start=acceptor.position,
                type="acceptor",
                colour=acceptor.colour,
            )
        )

    return Compiled(
        transcripts=compiled_transcripts,
        groups=compiled_groups,
        splicing_sites=splicing_sites,
        title=parsed_inputs.title,
    )
