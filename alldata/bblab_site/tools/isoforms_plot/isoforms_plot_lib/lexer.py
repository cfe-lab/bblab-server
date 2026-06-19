"""
Lexer handles encodings, line endings, and other low-level details of reading the CSV file, providing a clean interface for the parser to work with text lines regardless of the original file's format.
"""

from io import StringIO
from pathlib import Path
from typing import BinaryIO, TextIO
from multicsv import MultiCSVFile
import multicsv


def decode_bytes(content: bytes) -> str:
    """Try to decode bytes using multiple common encodings."""
    # Try common encodings in order of likelihood, starting with those that can fail
    # (so we detect them properly) and ending with latin-1 which accepts all bytes
    encodings = [
        "utf-8-sig",  # UTF-8 with BOM (Excel, modern tools)
        "utf-8",  # UTF-8 without BOM (most common)
        "cp1252",  # Windows Western European (common in Excel exports)
        "iso-8859-1",  # Latin-1 / ISO 8859-1 (Western European)
        "cp1250",  # Windows Central European
        "latin-1",  # ISO 8859-1 alias (accepts all byte sequences as fallback)
    ]

    for enc in encodings:
        try:
            return content.decode(enc)
        except (UnicodeDecodeError, LookupError) as err:
            last = err
            continue

    # If all encodings fail, raise an error
    raise last


def normalize_line_endings(content: str) -> str:
    """Normalize line endings to Unix-style (\\n).

    Handles:
    - Windows (\\r\\n) -> \\n
    - Old Mac (\\r) -> \\n
    - Unix (\\n) -> \\n (unchanged)
    """
    # Replace CRLF with LF first, then any remaining CR with LF
    content = content.replace("\r\n", "\n")
    content = content.replace("\r", "\n")
    return content


def open_csv_file(input: Path | TextIO | BinaryIO) -> multicsv.MultiCSVFile:
    if isinstance(input, Path):
        content_bytes = input.read_bytes()
        text_content = decode_bytes(content_bytes)
        text_content = normalize_line_endings(text_content)
        stream = StringIO(text_content)
        return multicsv.wrap(stream)
    else:
        content = input.read()

        # Handle bytes (from file uploads)
        if isinstance(content, bytes):
            content = decode_bytes(content)

        # Normalize line endings for all text content
        content = normalize_line_endings(content)
        stream = StringIO(content)
        return multicsv.wrap(stream)


def lex(file: Path | TextIO | BinaryIO) -> MultiCSVFile:
    return open_csv_file(file)
