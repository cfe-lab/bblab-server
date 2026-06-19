"""
The job of the compiler is to take parsed inputs and transform them into a form that the plotter can use.
This is where we do things like:
- assign transcripts to groups
- convert Fragment objects to tuples
- resolve "end" (None) to END_POS
"""

from collections import Counter
from dataclasses import dataclass
from typing import Literal, Optional, Sequence, Tuple

from .parser import AST, Transcript, SpliceSiteColour
from . import exceptions as ex

END_POS = 9719


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
    valid_internal_starts: set[int],
    valid_internal_ends: set[int],
    acceptor_colours: dict[int, Optional[SpliceSiteColour]],
    donor_colours: dict[int, Optional[SpliceSiteColour]],
) -> Tuple[Sequence[CompiledTranscript], Sequence[CompiledGroup]]:

    # Validate transcripts have fragments
    for i, transcript in enumerate(parsed_transcripts):
        if not transcript.fragments:
            raise ex.EmptyTranscriptError(transcript_index=i)

    # Convert transcripts to plotter format
    compiled_transcripts = []
    for i, transcript in enumerate(parsed_transcripts):
        # Convert fragments to CompiledFragment objects with colours
        num_fragments = len(transcript.fragments)
        compiled_parts = []
        for j, fragment in enumerate(transcript.fragments):
            start = fragment.start
            end = fragment.end if fragment.end is not None else END_POS

            # Bounds check: every coordinate must not exceed END_POS
            if start > END_POS:
                raise ex.FragmentStartOutOfBoundsError(
                    transcript_index=i,
                    fragment_index=j,
                    start_position=start,
                    max_position=END_POS,
                )
            if end > END_POS:
                raise ex.FragmentEndOutOfBoundsError(
                    transcript_index=i,
                    fragment_index=j,
                    end_position=end,
                    max_position=END_POS,
                )

            # Internal boundary check:
            # Non-first fragments must start at a declared acceptor site.
            # Non-last fragments must end at a declared donor site.
            if j != 0 and start not in valid_internal_starts:
                raise ex.InvalidFragmentStartError(
                    transcript_index=i,
                    fragment_index=j,
                    start_position=start,
                    valid_starts=sorted(valid_internal_starts),
                )
            if j != num_fragments - 1 and end not in valid_internal_ends:
                raise ex.InvalidFragmentEndError(
                    transcript_index=i,
                    fragment_index=j,
                    end_position=end,
                    valid_ends=sorted(valid_internal_ends),
                )

            # Determine fragment colour:
            # explicit annotation takes priority over splice-site derivation
            if fragment.colour is not None:
                fragment_colour = fragment.colour
            else:
                start_colour = acceptor_colours.get(start)
                end_colour = donor_colours.get(end)

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

                fragment_colour = start_colour or end_colour

            compiled_parts.append(
                CompiledFragment(start=start, end=end, colour=fragment_colour)
            )

        parts_tuple = tuple(compiled_parts)

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

        # Wrap N_observed in parentheses for display as comment
        comment = f"({transcript.N_observed})" if transcript.N_observed else None

        compiled_transcripts.append(
            CompiledTranscript(
                parts=parts_tuple,
                label=transcript.label,
                comment=comment,
            )
        )

    # Deduplicate consecutive labels
    # e.g., gag -> vpr -> vpr -> vpr becomes gag -> vpr -> None -> None
    prev_label = None
    deduplicated_transcripts: list[CompiledTranscript] = []
    for ct in compiled_transcripts:
        current_label = ct.label
        if current_label is not None and current_label == prev_label:
            # Remove duplicate consecutive label (keep comment intact)
            deduplicated_transcripts.append(
                CompiledTranscript(
                    parts=ct.parts,
                    label=None,
                    comment=ct.comment,
                )
            )
        else:
            deduplicated_transcripts.append(ct)
        prev_label = current_label if current_label is not None else prev_label

    compiled_transcripts = deduplicated_transcripts

    # Build groups structure
    # Groups are consecutive runs of transcripts with the same group value
    # Preserve order and allow the same group name to appear multiple times
    groups_list: list[tuple[str | None, int]] = []
    first_group = True
    last_group: str | None = None
    current_group_size = 0

    for transcript in parsed_transcripts:
        if first_group or transcript.group != last_group:
            if not first_group:
                groups_list.append((last_group, current_group_size))
            first_group = False
            last_group = transcript.group
            current_group_size = 0
        current_group_size += 1

    # Don't forget the final group
    if not first_group:
        groups_list.append((last_group, current_group_size))

    # Build CompiledGroup objects
    compiled_groups = [
        CompiledGroup(name=group_name, size=size)
        for group_name, size in groups_list
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
    - Fragment positions do not exceed END_POS
    - Non-first fragment starts match a declared acceptor
    - Non-last fragment ends match a declared donor
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

    # Build sets of valid internal boundary positions
    # Internal starts must be declared acceptor sites.
    # Internal ends must be declared donor sites.
    valid_internal_starts = {acceptor.position for acceptor in parsed_inputs.acceptors}
    valid_internal_ends = {donor.position for donor in parsed_inputs.donors}

    # Build colour mappings for splice sites (position -> colour)
    # Position 1 and END_POS have no associated colour (None)
    acceptor_colours: dict[int, Optional[SpliceSiteColour]] = {1: None}
    for acceptor in parsed_inputs.acceptors:
        acceptor_colours[acceptor.position] = acceptor.colour

    donor_colours: dict[int, Optional[SpliceSiteColour]] = {END_POS: None}
    for donor in parsed_inputs.donors:
        donor_colours[donor.position] = donor.colour

    compiled_transcripts, compiled_groups = compile_transcripts(
        parsed_inputs.transcripts,
        valid_internal_starts,
        valid_internal_ends,
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
