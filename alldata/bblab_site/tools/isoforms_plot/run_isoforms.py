import sys
import os

sys.path.append(os.environ.get("BBLAB_UTIL_PATH", "fail"))

import traceback
from pathlib import Path
from typing import TextIO

# Add the parent directory to sys.path to enable isoforms_plot imports
CURDIR = Path(__file__).parent.absolute()
if str(CURDIR) not in sys.path:
    sys.path.insert(0, str(CURDIR))

# Constants
OUTPUT_SVG = "/alldata/bblab_site/media/output.svg"
DEFAULT_CSV_PATH = Path(__file__).parent / "test_isoforms.csv"


def get_default_csv() -> str:
    """Return the default CSV content for download."""
    try:
        return DEFAULT_CSV_PATH.read_text(encoding="utf8")
    except Exception:
        return ""


# -- Main runner ----------------------------------------------------------


def run(csv_file: TextIO) -> dict:
    """Orchestrate plotting. Returns dict with results.

    Returns:
        dict with keys:
        - 'success': bool
        - 'svg_path': str (if success)
        - 'error_message': str (if not success)
        - 'error_details': str (if not success, traceback)
    """

    # Try to generate plot - all validation happens in the plotter
    try:
        import isoforms_plot.parser as parser
        import isoforms_plot.compiler as compiler
        import isoforms_plot.plotter as plotter
        import isoforms_plot.lexer as lexer

        lexed = lexer.lex(csv_file)
        parsed = parser.parse(lexed)
        compiled = compiler.compile(parsed)
        drawing = plotter.plot(
            compiled.transcripts,
            compiled.groups,
            compiled.splicing_sites,
            compiled.title,
        )
        drawing.save_svg(OUTPUT_SVG)

    except Exception as exc:
        return {
            "success": False,
            "error_message": str(exc),
            "error_details": traceback.format_exc(),
        }

    # Return success with SVG path
    return {"success": True, "svg_path": "/media/output.svg"}
