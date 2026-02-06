import sys
import os

sys.path.append(os.environ.get("BBLAB_UTIL_PATH", "fail"))

import io
import html
import traceback
from pathlib import Path
from typing import Tuple

# Add the parent directory to sys.path to enable isoforms_plot imports
CURDIR = Path(__file__).parent.absolute()
if str(CURDIR) not in sys.path:
    sys.path.insert(0, str(CURDIR))

# Constants
OUTPUT_SVG = "/alldata/bblab_site/media/output.svg"
DEFAULT_CSV_PATH = Path(__file__).parent / "test_isoforms.csv"


# -- Utility helpers -------------------------------------------------------
def _read_csv_text(csv_data) -> Tuple[str, str]:
    """Return CSV text or (None, error_message)."""
    try:
        if hasattr(csv_data, "read"):
            raw = csv_data.read()
            if isinstance(raw, bytes):
                raw = raw.decode("utf8")
            return raw, ""
        # allow path-like input
        text = Path(csv_data).read_text(encoding="utf8")
        return text, ""
    except Exception as exc:
        return "", f"Could not read input CSV: {html.escape(str(exc))}"


def get_default_csv() -> str:
    """Return the default CSV content for download."""
    try:
        return DEFAULT_CSV_PATH.read_text(encoding="utf8")
    except Exception:
        return ""


# -- Main runner ----------------------------------------------------------


def run(csv_data):
    """Orchestrate plotting. Returns generated site HTML."""
    import web_output

    website = web_output.Site("Isoforms Plot - Results", web_output.SITE_BOXED)
    website.set_footer('go back to <a href="/django/wiki/" >wiki</a>')

    # Add link to download default CSV
    website.send(
        "<div style='text-align:right;margin-bottom:16px;'>"
        "<a href='/django/isoforms/download_default/' "
        "style='display:inline-block;background:#5bc0de;color:#fff;padding:8px 14px;border-radius:4px;text-decoration:none;font-weight:500;'>"
        "Download Example CSV"
        "</a>"
        "</div>"
    )

    # Read CSV text
    csv_text, read_err = _read_csv_text(csv_data)
    if read_err:
        website.send(
            f"<div style='border:1px solid #d9534f;padding:12px;background:#f8d7da;color:#721c24;'>"
            f"<h2>Problem reading your file</h2>"
            f"<p>{read_err}</p>"
            f"<p>Please make sure you uploaded a CSV file and that it is readable.</p>"
            f"</div>"
        )
        return website.generate_site()

    # Try to generate plot - all validation happens in the plotter
    try:
        import isoforms_plot.parser as parser
        import isoforms_plot.compiler as compiler
        import isoforms_plot.plotter as plotter

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
        # Show error with simple display
        website.send("<h2 style='color:#a94442'>Error creating plot</h2>")
        website.send(
            f"<div style='border:1px solid #a94442;padding:12px;background:#f2dede;color:#a94442;'>"
            f"<p><strong>Error:</strong> {html.escape(str(exc))}</p>"
            f"</div>"
        )
        # Show traceback for debugging
        website.send(
            f"<details style='margin-top:10px;'>"
            f"<summary style='cursor:pointer;color:#666;'>Show technical details</summary>"
            f"<pre style='background:#f5f5f5;padding:10px;overflow:auto;font-size:11px;'>{html.escape(traceback.format_exc())}</pre>"
            f"</details>"
        )
        website.send(
            "<p>Please check your CSV file and try again. "
            "You can download the example CSV above to see the expected format.</p>"
        )
        return website.generate_site()

    # Show SVG output
    website.send("<h2>Your Plot</h2>")
    website.send("<img width='100%' src='/media/output.svg' alt='Output svg' />")

    # Add download button
    website.send(
        "<div style='text-align:center;margin:16px 0;'>"
        "<a href='/media/output.svg' download='isoforms.svg' "
        "style='display:inline-block;background:#5cb85c;color:#fff;padding:12px 24px;border-radius:6px;"
        "text-decoration:none;font-weight:600;box-shadow:0 4px 10px rgba(0,0,0,0.12);'>"
        "Download SVG"
        "</a>"
        "</div>"
    )

    return website.generate_site()
