import sys
import os
sys.path.append(os.environ.get('BBLAB_UTIL_PATH', 'fail'))

import io
import csv
import html
import json
import traceback
from pathlib import Path
from typing import List, Tuple

import web_output
import mailer

# Constants
REQUIRED_COLUMNS = ['samp_name', 'ref_start', 'ref_end', 'defect', 'is_defective', 'is_inverted']
MAX_INSPECT_ROWS = 2000
OUTPUT_SVG = '/alldata/bblab_site/media/output.svg'


# -- Utility helpers -------------------------------------------------------
def _make_box(title: str, items: List[str], border: str, bg: str, text_color: str) -> str:
    if not items:
        return ''
    lis = ''.join(f"<li>{html.escape(s)}</li>" for s in items)
    return (
        f"<div style='border:1px solid {border};padding:12px;background:{bg};color:{text_color};margin:8px 0;'>"
        f"<strong>{html.escape(title)} ({len(items)})</strong>"
        f"<ul style='margin:6px 0 0 18px;padding:0;'>{lis}</ul></div>"
    )


def _read_csv_text(csv_data) -> Tuple[str, str]:
    """Return CSV text or (None, error_message)."""
    try:
        if hasattr(csv_data, 'read'):
            raw = csv_data.read()
            if isinstance(raw, bytes):
                raw = raw.decode('utf8')
            return raw, ''
        # allow path-like input
        text = Path(csv_data).read_text(encoding='utf8')
        return text, ''
    except Exception as exc:
        return '', f"Could not read input CSV: {html.escape(str(exc))}"


def _validate_csv_text(csv_text: str) -> Tuple[List[str], List[str]]:
    """Validate CSV header and a limited number of rows.
    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []

    stream = io.StringIO(csv_text)
    try:
        reader = csv.DictReader(stream)
    except Exception as exc:
        errors.append(f"Failed to parse CSV header: {str(exc)}")
        return errors, warnings

    headers = reader.fieldnames or []
    if not headers:
        errors.append("No CSV header found or file is empty.")
        return errors, warnings

    for col in REQUIRED_COLUMNS:
        if col not in headers:
            errors.append(f"Missing required column: '{col}'")

    # Inspect rows for basic type/value checks
    stream.seek(0)
    reader = csv.DictReader(stream)

    inspected = 0
    for i, row in enumerate(reader, start=1):
        if inspected >= MAX_INSPECT_ROWS:
            break
        inspected += 1
        # skip blank rows
        if not any((v and v.strip() for v in row.values())):
            continue

        samp = (row.get('samp_name') or '').strip()
        if not samp:
            errors.append(f"Row {i}: missing sample name ('samp_name').")

        rs = (row.get('ref_start') or '').strip()
        re = (row.get('ref_end') or '').strip()
        if not rs or not re:
            errors.append(f"Row {i}: missing 'ref_start' or 'ref_end'.")
            continue
        try:
            rs_i = int(rs)
            re_i = int(re)
            if rs_i < 0 or re_i < 0:
                warnings.append(f"Row {i}: start/end negative: {rs}/{re}.")
            if rs_i >= re_i:
                warnings.append(f"Row {i}: 'ref_start' >= 'ref_end' ({rs_i} >= {re_i}).")
        except ValueError:
            errors.append(f"Row {i}: 'ref_start' and 'ref_end' must be integers (got '{html.escape(rs)}'/'{html.escape(re)}').")
            continue

        defect_val = (row.get('defect') or '').strip()
        if not defect_val:
            warnings.append(f"Row {i}: empty 'defect' field.")

        for bool_col in ('is_defective', 'is_inverted'):
            val = (row.get(bool_col) or '').strip().lower()
            if val and val not in ('0', '1', 'true', 'false', 't', 'f'):
                warnings.append(
                    f"Row {i}: column '{bool_col}' has non-standard value '{html.escape(row.get(bool_col) or '')}'."
                    " Expected 0/1 or True/False."
                )

    return errors, warnings


def _import_plot_module():
    # Import locally to avoid expensive imports before validation
    try:
        from . import proviral_landscape_plot
        return proviral_landscape_plot, ''
    except Exception as exc:
        return None, str(exc)


# -- Main runner ----------------------------------------------------------

def run(csv_data, analysis_id, email_address_string):
    """Orchestrate validation, plotting and notification. Returns generated site HTML."""
    website = web_output.Site("Proviral Landscape Plot - Results", web_output.SITE_BOXED)
    website.set_footer('go back to <a href="/django/wiki/" >wiki</a>')

    # Read CSV text
    csv_text, read_err = _read_csv_text(csv_data)
    if read_err:
        website.send(
            f"<div style='border:1px solid #d9534f;padding:12px;background:#f8d7da;color:#721c24;'><h2>Critical error</h2><p>{html.escape(read_err)}</p></div>"
        )
        return website.generate_site()

    # Validate
    errors, warnings = _validate_csv_text(csv_text)

    # Present validation results
    if errors:
        website.send("<h1 style='color:#a94442'>Input validation failed</h1>")
        website.send(_make_box('Errors', errors, '#a94442', '#f2dede', '#a94442'))
        if warnings:
            website.send(_make_box('Warnings', warnings, '#f0ad4e', '#fcf8e3', '#8a6d3b'))
        website.send("<p>Please correct the CSV file and try again. No plot was generated.</p>")
        return website.generate_site()

    if warnings:
        website.send("<h2 style='color:#8a6d3b'>Validation warnings</h2>")
        website.send(_make_box('Warnings', warnings, '#f0ad4e', '#fcf8e3', '#8a6d3b'))
        website.send("<p>The plot will be generated but some rows may be unexpected. Inspect the warnings above.</p>")

    # Import plotting module after successful validation
    plot_mod, import_err = _import_plot_module()
    if plot_mod is None:
        website.send("<h2 style='color:#a94442'>Internal error</h2>")
        website.send(
            f"<div style='border:1px solid #a94442;padding:12px;background:#f2dede;color:#a94442;'><p>Failed to import plotting module: {html.escape(import_err)}</p></div>"
        )
        website.send(f"<pre style='background:#fff;padding:8px;border:1px solid #eee;'>{html.escape(traceback.format_exc())}</pre>")
        return website.generate_site()

    # Generate plot
    try:
        input_stream = io.StringIO(csv_text)
        plot_mod.create_proviral_plot(input_stream, OUTPUT_SVG)
    except Exception as exc:
        website.send("<h2 style='color:#a94442'>Plot generation failed</h2>")
        website.send(
            f"<div style='border:1px solid #a94442;padding:12px;background:#f2dede;color:#a94442;'><p>Unexpected error while creating plot: {html.escape(str(exc))}</p></div>"
        )
        website.send(f"<pre style='background:#fff;padding:8px;border:1px solid #eee;'>{html.escape(traceback.format_exc())}</pre>")
        return website.generate_site()

    # Show SVG output
    website.send(f"<img width='100%' src='/media/output.svg' alt='Output svg' />")

    # Short description for email
    short_description = analysis_id or ''
    if len(short_description) > 30:
        short_description = short_description[:30] + "..."

    # Email subject and body
    subject_line = "Proviral Landscape Plot Results"
    if short_description:
        subject_line += f" - {short_description}"
    quoted_description = json.dumps(short_description)
    msg_body = f"Your landscape plot, described as {quoted_description}, is ready. See the attachment."

    # Attach and send email
    try:
        svg_content = Path(OUTPUT_SVG).read_text(encoding='utf8')
        plot_file = mailer.create_file(short_description, 'svg', svg_content)
        if mailer.send_sfu_email("proviral_landscape_plot", email_address_string, subject_line, msg_body, [plot_file]) == 0:
            website.send(("An email has been sent to <b>{}</b> with your image." "<br>Make sure <b>{}</b> is spelled correctly.").format(email_address_string, email_address_string))
    except Exception:
        # Non-fatal: show warning but continue
        website.send("<div style='border:1px solid #f0ad4e;padding:10px;background:#fcf8e3;color:#8a6d3b;'><strong>Warning</strong>: failed to prepare or send email.</div>")
        website.send(f"<pre style='background:#fff;padding:8px;border:1px solid #eee;'>{html.escape(traceback.format_exc())}</pre>")

    return website.generate_site()
