"""
The job of the compiler is to take parsed inputs and transform them into a form that the plotter can use.
This is where we do things like:
- assign transcripts to groups
- convert Fragment objects to tuples
- resolve "end" (None) to END_POS
"""

from collections import Counter
from typing import Any, Sequence

from isoforms_plot.parser import AST, Transcript

END_POS = 9632

# default positions of splicing sites in NL43.
SPLICING_SITES = [
    {"name": "D1", "start": 743, "type": "donor"},
    {"name": "D2", "start": 4962, "type": "donor"},
    {"name": "D2b", "start": 5058, "type": "donor"},
    {"name": "D3", "start": 5463, "type": "donor"},
    {"name": "D4", "start": 6046, "type": "donor"},
    {"name": "A1", "start": 4913, "type": "acceptor"},
    {"name": "A2", "start": 5390, "type": "acceptor"},
    {"name": "A3", "start": 5777, "type": "acceptor"},
    {"name": "A4c", "start": 5936, "type": "acceptor"},
    {"name": "A4a", "start": 5954, "type": "acceptor"},
    {"name": "A4b", "start": 5960, "type": "acceptor"},
    {"name": "A5", "start": 5976, "type": "acceptor"},
    {"name": "A7", "start": 8369, "type": "acceptor"},
]


def compile_transcripts(
    parsed_transcripts: Sequence[Transcript],
) -> list[dict[str, Any]]:

    # Convert transcripts to plotter format
    compiled_transcripts = []
    for transcript in parsed_transcripts:
        # Convert fragments to parts
        parts = []
        for fragment in transcript.fragments:
            start = fragment.start
            end = fragment.end if fragment.end is not None else END_POS
            parts.append((start, end))

        # Build transcript dict
        transcript_dict = {"parts": parts}
        if transcript.label is not None:
            transcript_dict["label"] = transcript.label
        if transcript.comment is not None:
            transcript_dict["comment"] = transcript.comment

        compiled_transcripts.append(transcript_dict)

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
    compiled_groups = []
    for group_name in groups_order:
        compiled_groups.append(
            {
                "name": group_name,
                "size": group_counts[group_name],
            }
        )

    return compiled_transcripts, compiled_groups


def compile(parsed_inputs: AST) -> dict[str, Any]:
    """
    Compile parsed AST into plotter-ready format.

    Transforms:
    - Fragment(start, end) → (start, end) tuple where end=None becomes END_POS
    - Transcript objects → dicts with 'parts', 'label', 'comment'
    - Groups transcripts by their 'group' attribute
    """

    compiled_transcripts, compiled_groups = compile_transcripts(
        parsed_inputs.transcripts
    )

    return {
        "splicing_sites": SPLICING_SITES,
        "transcripts": compiled_transcripts,
        "groups": compiled_groups,
        "title": parsed_inputs.title,
    }
