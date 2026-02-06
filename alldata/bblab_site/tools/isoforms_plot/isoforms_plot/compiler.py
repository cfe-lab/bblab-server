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

from isoforms_plot.parser import AST, Transcript

END_POS = 9632


@dataclass(frozen=True)
class CompiledSplicingSite:
    name: str
    start: int
    type: Literal["donor", "acceptor"]


@dataclass(frozen=True)
class CompiledTranscript:
    parts: Sequence[Tuple[int, int]]
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
) -> Tuple[Sequence[CompiledTranscript], Sequence[CompiledGroup]]:

    # Convert transcripts to plotter format
    compiled_transcripts = []
    for transcript in parsed_transcripts:
        # Convert fragments to parts
        parts = tuple(
            (fragment.start, fragment.end if fragment.end is not None else END_POS)
            for fragment in transcript.fragments
        )

        compiled_transcripts.append(
            CompiledTranscript(
                parts=parts,
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
    seen = set()
    for transcript in parsed_transcripts:
        if transcript.group not in seen:
            groups_order.append(transcript.group)
            seen.add(transcript.group)

    # Count transcripts per group
    group_counts = Counter(t.group for t in parsed_transcripts)

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
    - Fragment(start, end) → (start, end) tuple where end=None becomes END_POS
    - Transcript objects → CompiledTranscript dataclasses
    - Groups transcripts by their 'group' attribute into CompiledGroup dataclasses
    - Donor/Acceptor objects → CompiledSplicingSite dataclasses
    """

    compiled_transcripts, compiled_groups = compile_transcripts(
        parsed_inputs.transcripts
    )

    # Convert donors and acceptors to splicing sites
    splicing_sites = []
    for donor in parsed_inputs.donors:
        splicing_sites.append(
            CompiledSplicingSite(name=donor.name, start=donor.position, type="donor")
        )
    for acceptor in parsed_inputs.acceptors:
        splicing_sites.append(
            CompiledSplicingSite(
                name=acceptor.name, start=acceptor.position, type="acceptor"
            )
        )

    return Compiled(
        transcripts=compiled_transcripts,
        groups=compiled_groups,
        splicing_sites=splicing_sites,
        title=parsed_inputs.title,
    )
