import sys
import os

sys.path.append(os.environ.get("BBLAB_UTIL_PATH", "fail"))

import io
import traceback
from pathlib import Path

# Add the parent directory to sys.path to enable isoforms_plot imports
CURDIR = Path(__file__).parent.absolute()
if str(CURDIR) not in sys.path:
    sys.path.insert(0, str(CURDIR))

# Constants
OUTPUT_SVG = "/alldata/bblab_site/media/output.svg"
DEFAULT_CSV_PATH = Path(__file__).parent / "test_isoforms.csv"


# -- Utility helpers -------------------------------------------------------
def _read_csv_text(csv_data) -> str:
    """Return CSV text or (None, error_message)."""
    if hasattr(csv_data, "read"):
        raw = csv_data.read()
        if isinstance(raw, bytes):
            raw = raw.decode("utf8")
        return raw
    # allow path-like input
    text = Path(csv_data).read_text(encoding="utf8")
    return text


def get_default_csv() -> str:
    """Return the default CSV content for download."""
    try:
        return DEFAULT_CSV_PATH.read_text(encoding="utf8")
    except Exception:
        return ""


# -- Main runner ----------------------------------------------------------


def run(csv_file):
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

        # Read CSV text
        file_bytes = csv_file.read()
        csv_data = file_bytes.decode("utf-8")
        csv_text = _read_csv_text(csv_data)

        # Parse
        input_stream = io.StringIO(csv_text)
        parsed = parser.parse(input_stream)

        # Compile
        compiled = compiler.compile(parsed)

        # Plot
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
