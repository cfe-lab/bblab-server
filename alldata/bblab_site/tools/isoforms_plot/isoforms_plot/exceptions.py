"""
Exception classes for isoforms_plot.

Parse Errors: Raised during CSV parsing when input format is invalid.
Compile Errors: Raised during compilation when semantic constraints are violated.
"""

from typing import Any, Dict, Sequence

# ============================================================================
# PARSE ERRORS - Raised by parser.py when input format is invalid
# ============================================================================


class MissingFragmentsError(ValueError):
    """Raised when a transcript row has no fragments field."""

    def __init__(self, row: Dict[str, object]) -> None:
        self.row = row
        super().__init__(
            f"Missing 'fragments' field in transcript row. Row data: {row}"
        )


class InvalidDashPatternError(ValueError):
    """Raised when a fragment doesn't follow 'start-end' format."""

    def __init__(self, fragment_str: str, previous_str: str, next_str: str) -> None:
        self.fragment_str = fragment_str
        self.previous_str = previous_str
        self.next_str = next_str
        super().__init__(
            f"Invalid fragment string: '{fragment_str}'. Expected format 'start-end'.\n"
            f"Context: {previous_str}|HERE|{next_str}"
        )


class EmptyFragmentError(ValueError):
    """Raised when a fragment string is empty after stripping."""

    def __init__(self, fragment_str: str, previous_str: str, next_str: str) -> None:
        self.fragment_str = fragment_str
        self.previous_str = previous_str
        self.next_str = next_str
        super().__init__(
            f"Empty fragment string found.\n"
            f"Context: {previous_str}|HERE|{next_str}"
        )


class NotIntegerStartError(ValueError):
    """Raised when fragment start position is not a valid integer."""

    def __init__(
        self, start_str: str, fragment_str: str, previous_str: str, next_str: str
    ) -> None:
        self.start_str = start_str
        self.fragment_str = fragment_str
        self.previous_str = previous_str
        self.next_str = next_str
        super().__init__(
            f"Fragment start '{start_str}' is not a valid integer in fragment '{fragment_str}'.\n"
            f"Context: {previous_str}|HERE|{next_str}"
        )


class NotPositiveStartError(ValueError):
    """Raised when fragment start position is not positive (< 1)."""

    def __init__(
        self, start: int, fragment_str: str, previous_str: str, next_str: str
    ) -> None:
        self.start = start
        self.fragment_str = fragment_str
        self.previous_str = previous_str
        self.next_str = next_str
        super().__init__(
            f"Fragment start {start} must be positive (>= 1) in fragment '{fragment_str}'.\n"
            f"Context: {previous_str}|HERE|{next_str}"
        )


class NotIntegerEndError(ValueError):
    """Raised when fragment end position is not a valid integer (and not 'end' keyword)."""

    def __init__(
        self, end_str: str, fragment_str: str, previous_str: str, next_str: str
    ) -> None:
        self.end_str = end_str
        self.fragment_str = fragment_str
        self.previous_str = previous_str
        self.next_str = next_str
        super().__init__(
            f"Fragment end '{end_str}' is not a valid integer or 'end' keyword in fragment '{fragment_str}'.\n"
            f"Context: {previous_str}|HERE|{next_str}"
        )


class NotPositiveEndError(ValueError):
    """Raised when fragment end position is not positive (< 1)."""

    def __init__(
        self, end: int, fragment_str: str, previous_str: str, next_str: str
    ) -> None:
        self.end = end
        self.fragment_str = fragment_str
        self.previous_str = previous_str
        self.next_str = next_str
        super().__init__(
            f"Fragment end {end} must be positive (>= 1) in fragment '{fragment_str}'.\n"
            f"Context: {previous_str}|HERE|{next_str}"
        )


class EndLessThanStartError(ValueError):
    """Raised when fragment end position is less than start position."""

    def __init__(
        self, start: int, end: int, fragment_str: str, previous_str: str, next_str: str
    ) -> None:
        self.start = start
        self.end = end
        self.fragment_str = fragment_str
        self.previous_str = previous_str
        self.next_str = next_str
        super().__init__(
            f"Fragment end {end} cannot be less than start {start} in fragment '{fragment_str}'.\n"
            f"Context: {previous_str}|HERE|{next_str}"
        )


class TitleSectionTooManyNonEmptyValuesError(ValueError):
    """Raised when [title] section has multiple non-empty rows."""

    def __init__(self, nonempty: Sequence[Sequence[str]]) -> None:
        self.nonempty = nonempty
        super().__init__(
            f"Title section should contain at most one non-empty value, but found {len(nonempty)}: {nonempty}"
        )


class MissingDonorNameError(ValueError):
    """Raised when a donor row has no name field."""

    def __init__(self, row: Dict[str, object]) -> None:
        self.row = row
        super().__init__(f"Missing 'name' field in donor row. Row data: {row}")


class MissingDonorPositionError(ValueError):
    """Raised when a donor row has no position field."""

    def __init__(self, donor_name: str, row: Dict[str, object]) -> None:
        self.donor_name = donor_name
        self.row = row
        super().__init__(
            f"Missing 'position' field for donor '{donor_name}'. Row data: {row}"
        )


class InvalidDonorPositionError(ValueError):
    """Raised when a donor position is not a valid integer."""

    def __init__(
        self, position_str: str, donor_name: str, row: Dict[str, object]
    ) -> None:
        self.position_str = position_str
        self.donor_name = donor_name
        self.row = row
        super().__init__(
            f"Invalid position '{position_str}' for donor '{donor_name}'. "
            f"Position must be an integer. Row data: {row}"
        )


class MissingAcceptorNameError(ValueError):
    """Raised when an acceptor row has no name field."""

    def __init__(self, row: Dict[str, object]) -> None:
        self.row = row
        super().__init__(f"Missing 'name' field in acceptor row. Row data: {row}")


class MissingAcceptorPositionError(ValueError):
    """Raised when an acceptor row has no position field."""

    def __init__(self, acceptor_name: str, row: Dict[str, object]) -> None:
        self.acceptor_name = acceptor_name
        self.row = row
        super().__init__(
            f"Missing 'position' field for acceptor '{acceptor_name}'. Row data: {row}"
        )


class InvalidAcceptorPositionError(ValueError):
    """Raised when an acceptor position is not a valid integer."""

    def __init__(
        self, position_str: str, acceptor_name: str, row: Dict[str, object]
    ) -> None:
        self.position_str = position_str
        self.acceptor_name = acceptor_name
        self.row = row
        super().__init__(
            f"Invalid position '{position_str}' for acceptor '{acceptor_name}'. "
            f"Position must be an integer. Row data: {row}"
        )


class MissingTranscriptsSectionError(ValueError):
    """Raised when CSV file is missing required [transcripts] section."""

    def __init__(self, sections: Dict[str, str]) -> None:
        self.sections = sections
        super().__init__(
            f"Missing required [transcripts] section in CSV file. "
            f"Found sections: {list(sections.keys())}"
        )


class MissingDonorsSectionError(ValueError):
    """Raised when CSV file is missing required [donors] section."""

    def __init__(self, sections: Dict[str, str]) -> None:
        self.sections = sections
        super().__init__(
            f"Missing required [donors] section in CSV file. "
            f"Found sections: {list(sections.keys())}"
        )


class MissingAcceptorsSectionError(ValueError):
    """Raised when CSV file is missing required [acceptors] section."""

    def __init__(self, sections: Dict[str, str]) -> None:
        self.sections = sections
        super().__init__(
            f"Missing required [acceptors] section in CSV file. "
            f"Found sections: {list(sections.keys())}"
        )


class MultipleSectionsWithSameNameError(ValueError):
    """Raised when CSV file contains multiple sections with the same name (case-insensitive)."""

    def __init__(self, multisections: Dict[str, Sequence[str]]) -> None:
        self.multisections = multisections
        duplicates = [
            matches for name, matches in multisections.items() if len(matches) > 1
        ]
        super().__init__(
            f"Multiple sections with the same name found (case-insensitive): {duplicates}"
        )


# ============================================================================
# COMPILE ERRORS - Raised by compiler.py when semantic constraints are violated
# ============================================================================


class DuplicateDonorNameError(ValueError):
    """Raised when multiple donors share the same name."""

    def __init__(self, name: str, positions: Sequence[int]) -> None:
        self.name = name
        self.positions = positions
        super().__init__(
            f"Duplicate donor name '{name}' found at positions: {positions}. "
            f"Each donor must have a unique name."
        )


class DuplicateAcceptorNameError(ValueError):
    """Raised when multiple acceptors share the same name."""

    def __init__(self, name: str, positions: Sequence[int]) -> None:
        self.name = name
        self.positions = positions
        super().__init__(
            f"Duplicate acceptor name '{name}' found at positions: {positions}. "
            f"Each acceptor must have a unique name."
        )


class EmptyTranscriptError(ValueError):
    """Raised when a transcript has no fragments (empty parts)."""

    def __init__(self, transcript_index: int) -> None:
        self.transcript_index = transcript_index
        super().__init__(
            f"Transcript at index {transcript_index + 1} has no fragments. "
            f"Each transcript must have at least one fragment."
        )


class OverlappingFragmentsError(ValueError):
    """Raised when fragments in a transcript overlap."""

    def __init__(
        self,
        transcript_index: int,
        fragment_index: int,
        current_fragment: tuple,
        next_fragment: tuple,
    ) -> None:
        self.transcript_index = transcript_index
        self.fragment_index = fragment_index
        self.current_fragment = current_fragment
        self.next_fragment = next_fragment
        super().__init__(
            f"Overlapping fragments in transcript {transcript_index + 1}: "
            f"fragment {fragment_index + 1} {current_fragment} overlaps with "
            f"fragment {fragment_index + 2} {next_fragment}. "
            f"Fragment end ({current_fragment[1]}) must be less than next fragment start ({next_fragment[0]})."
        )


class InvalidFragmentStartError(ValueError):
    """Raised when a fragment starts at a position that is not 1 or an acceptor site."""

    def __init__(
        self,
        transcript_index: int,
        fragment_index: int,
        start_position: int,
        valid_starts: Sequence[int],
    ) -> None:
        self.transcript_index = transcript_index
        self.fragment_index = fragment_index
        self.start_position = start_position
        self.valid_starts = valid_starts
        valid_starts_str = ", ".join(map(str, sorted(valid_starts)))
        super().__init__(
            f"Invalid fragment start in transcript {transcript_index + 1}, fragment {fragment_index + 1}: "
            f"position {start_position} is not a valid start position. "
            f"Fragments must start at position 1 or at an acceptor site. "
            f"Valid start positions: {valid_starts_str}."
        )


class InvalidFragmentEndError(ValueError):
    """Raised when a fragment ends at a position that is not END_POS or a donor site."""

    def __init__(
        self,
        transcript_index: int,
        fragment_index: int,
        end_position: int,
        valid_ends: Sequence[int],
    ) -> None:
        self.transcript_index = transcript_index
        self.fragment_index = fragment_index
        self.end_position = end_position
        self.valid_ends = valid_ends
        valid_ends_str = ", ".join(map(str, sorted(valid_ends)))
        super().__init__(
            f"Invalid fragment end in transcript {transcript_index + 1}, fragment {fragment_index + 1}: "
            f"position {end_position} is not a valid end position. "
            f"Fragments must end at a donor site or use 'end' keyword. "
            f"Valid end positions: {valid_ends_str}."
        )


class InvalidSpliceSiteColourError(ValueError):
    """Raised when a splice site has an invalid colour (not in the allowed list)."""

    def __init__(
        self,
        site_type: str,
        site_name: str,
        colour: str,
        allowed_colours: Sequence[str],
        row: Dict[str, Any],
    ) -> None:
        self.site_type = site_type
        self.site_name = site_name
        self.colour = colour
        self.allowed_colours = allowed_colours
        self.row = row
        super().__init__(
            f"Invalid colour '{colour}' for {site_type} '{site_name}'. "
            f"Allowed colours are: {', '.join(allowed_colours)}. "
            f"Row data: {row}"
        )


class ConflictingFragmentColoursError(ValueError):
    """Raised when a fragment touches two splice sites with different colours."""

    def __init__(
        self,
        transcript_index: int,
        fragment_index: int,
        start_position: int,
        end_position: int,
        start_colour: str,
        end_colour: str,
    ) -> None:
        self.transcript_index = transcript_index
        self.fragment_index = fragment_index
        self.start_position = start_position
        self.end_position = end_position
        self.start_colour = start_colour
        self.end_colour = end_colour
        super().__init__(
            f"Conflicting colours for fragment in transcript {transcript_index + 1}, fragment {fragment_index + 1}: "
            f"fragment {start_position}-{end_position} touches splice sites with different colours. "
            f"Start position {start_position} has colour '{start_colour}', "
            f"end position {end_position} has colour '{end_colour}'. "
            f"A fragment cannot have two different colours."
        )


AnyError = (
    MissingFragmentsError
    | InvalidDashPatternError
    | EmptyFragmentError
    | NotIntegerStartError
    | NotPositiveStartError
    | NotIntegerEndError
    | NotPositiveEndError
    | EndLessThanStartError
    | TitleSectionTooManyNonEmptyValuesError
    | MissingDonorNameError
    | MissingDonorPositionError
    | InvalidDonorPositionError
    | MissingAcceptorNameError
    | MissingAcceptorPositionError
    | InvalidAcceptorPositionError
    | MissingTranscriptsSectionError
    | MissingDonorsSectionError
    | MissingAcceptorsSectionError
    | DuplicateDonorNameError
    | DuplicateAcceptorNameError
    | EmptyTranscriptError
    | OverlappingFragmentsError
    | InvalidFragmentStartError
    | InvalidFragmentEndError
)
