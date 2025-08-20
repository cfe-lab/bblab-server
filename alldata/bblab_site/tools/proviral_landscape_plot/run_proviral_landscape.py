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
import difflib

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


def _highlight_differences(expected: str, found: str) -> Tuple[str, str]:
    """Return (expected_html, found_html) with differing characters highlighted.

    Use SequenceMatcher opcodes to align the two strings so only the actual
    differing characters are highlighted (handles insertions/deletions/replaces)
    rather than highlighting everything after the first mismatch.
    """
    if expected is None:
        expected = ''
    if found is None:
        found = ''

    sm = difflib.SequenceMatcher(None, expected, found)
    exp_parts = []
    found_parts = []

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            # matching run: add as-is
            exp_parts.append(html.escape(expected[i1:i2]))
            found_parts.append(html.escape(found[j1:j2]))
        elif tag == 'replace':
            # differing run of same length (or similar) -> highlight both sides
            exp_sub = html.escape(expected[i1:i2])
            found_sub = html.escape(found[j1:j2])
            exp_parts.append(f"<span style='color:#d9534f;font-weight:bold'>{exp_sub}</span>")
            found_parts.append(f"<span style='color:#d9534f;font-weight:bold'>{found_sub}</span>")
        elif tag == 'delete':
            # expected has extra characters that are missing in found
            exp_sub = html.escape(expected[i1:i2])
            # in the 'found' display, insert visible zero-width placeholders so alignment
            # visually indicates missing characters
            placeholders = ''.join("<span style='color:#d9534f;font-weight:bold'>&#8203;</span>" for _ in range(i2 - i1))
            exp_parts.append(f"<span style='color:#d9534f;font-weight:bold'>{exp_sub}</span>")
            found_parts.append(placeholders)
        elif tag == 'insert':
            # found has extra characters that are missing in expected
            found_sub = html.escape(found[j1:j2])
            placeholders = ''.join("<span style='color:#d9534f;font-weight:bold'>&#8203;</span>" for _ in range(j2 - j1))
            exp_parts.append(placeholders)
            found_parts.append(f"<span style='color:#d9534f;font-weight:bold'>{found_sub}</span>")

    return ''.join(exp_parts), ''.join(found_parts)


def _validate_csv_text(csv_text: str) -> Tuple[List[str], List[str], List[str]]:
    """Validate CSV header and a limited number of rows.
    Returns (errors, warnings, suggestions_html).
    """
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []

    stream = io.StringIO(csv_text)
    try:
        reader = csv.DictReader(stream)
    except Exception as exc:
        errors.append(f"Failed to parse CSV header: {str(exc)}")
        return errors, warnings, suggestions

    headers = reader.fieldnames or []
    if not headers:
        errors.append("No CSV header found or file is empty.")
        return errors, warnings, suggestions

    # Track which columns are actually present so we don't emit cascading row-level
    # errors when a required column is missing (e.g., if 'samp_name' is absent, don't
    # complain about every row missing a sample name — the header-level error is enough).
    present_columns = set(headers)

    for col in REQUIRED_COLUMNS:
        if col not in headers:
            errors.append(f"Missing required column: '{col}'")

            # normalize helper
            def _norm(s: str) -> str:
                if s is None:
                    return ''
                s2 = s.strip()
                if s2.startswith('\ufeff'):
                    s2 = s2.lstrip('\ufeff')
                return s2.lower()

            col_norm = _norm(col)
            normalized = [(h, _norm(h)) for h in headers]

            # simple Levenshtein distance implementation for short header names
            def _levenshtein_distance(a: str, b: str) -> int:
                if a == b:
                    return 0
                la, lb = len(a), len(b)
                if la == 0:
                    return lb
                if lb == 0:
                    return la
                prev = list(range(lb + 1))
                for i, ca in enumerate(a, start=1):
                    cur = [i] + [0] * lb
                    for j, cb in enumerate(b, start=1):
                        cost = 0 if ca == cb else 1
                        cur[j] = min(prev[j] + 1, cur[j-1] + 1, prev[j-1] + cost)
                    prev = cur
                return prev[lb]

            candidates = []
            for orig, norm in normalized:
                try:
                    # Levenshtein-based ratio
                    dist = _levenshtein_distance(col_norm, norm)
                    maxlen = max(1, len(col_norm), len(norm))
                    lev_ratio = 1.0 - (dist / maxlen)
                except Exception:
                    lev_ratio = 0.0
                try:
                    seq_ratio = difflib.SequenceMatcher(None, col_norm, norm).ratio()
                except Exception:
                    seq_ratio = 0.0
                # combined score prefers the stronger signal
                score = max(lev_ratio, seq_ratio)
                candidates.append((score, orig))

            # sort by score descending
            candidates.sort(key=lambda x: x[0], reverse=True)
            # threshold for suggesting a possible typo match
            ratio_threshold = 0.55
            suggested = [h for r, h in candidates if r >= ratio_threshold][:3]
            if suggested:
                for m in suggested:
                    exp_h, found_h = _highlight_differences(col, m)
                    # only show visible-whitespace view if either side has leading/trailing spaces or tabs
                    show_ws = _has_visible_whitespace(col) or _has_visible_whitespace(m)
                    # build the compact boxed preview for the two names
                    boxed_preview = _boxed_column_preview(exp_h, found_h)
                    if show_ws:
                        vis_exp = _visible_whitespace_html(col)
                        vis_found = _visible_whitespace_html(m)
                        # use the same boxed preview for the visible-whitespace view
                        vis_boxed = _boxed_column_preview(vis_exp, vis_found)
                        suggestions.append(
                            "<div style='border:1px dashed #31708f;padding:10px;background:#d9edf7;color:#31708f;margin:6px 0;'>"
                            f"<strong>Possible header match for '{html.escape(col)}'</strong>"
                            f"{boxed_preview}"
                            f"<div style='margin-top:8px;'><em>Visible-whitespace view</em>" \
                            f"{vis_boxed}</div>"
                            "</div>"
                        )
                    else:
                        suggestions.append(
                            "<div style='border:1px dashed #31708f;padding:10px;background:#d9edf7;color:#31708f;margin:6px 0;'>"
                            f"<strong>Possible header match for '{html.escape(col)}'</strong>"
                            f"{boxed_preview}"
                            "</div>"
                        )
            else:
                # as a fallback, show the top candidate (even if below threshold) to aid debugging
                if candidates:
                    top_score, top_candidate = candidates[0]
                    # include visible-whitespace markers only if needed
                    show_ws = _has_visible_whitespace(col) or _has_visible_whitespace(top_candidate)
                    suggestions.append(f"Debug: top candidate for '{col}' is '{html.escape(top_candidate)}' with score {top_score:.3f}")
                    if top_score > 0:
                        exp_h, found_h = _highlight_differences(col, top_candidate)
                        boxed_preview_fb = _boxed_column_preview(exp_h, found_h)
                        if show_ws:
                            vis_top = _visible_whitespace_html(top_candidate)
                            vis_col = _visible_whitespace_html(col)
                            # show visible-whitespace using the same boxed layout
                            vis_boxed_fb = _boxed_column_preview(vis_col, vis_top)
                            suggestions.append(
                                "<div style='border:1px dashed #eee;padding:10px;background:#f7f7f7;color:#555;margin:6px 0;'>"
                                f"<strong>Closest header to '{html.escape(col)}' is '{html.escape(top_candidate)}' (score {top_score:.2f})</strong>"
                                f"{boxed_preview_fb}"
                                f"<div style='margin-top:8px;'><em>Visible-whitespace view</em>{vis_boxed_fb}</div>"
                                "</div>"
                            )
                        else:
                            suggestions.append(
                                "<div style='border:1px dashed #eee;padding:10px;background:#f7f7f7;color:#555;margin:6px 0;'>"
                                f"<strong>Closest header to '{html.escape(col)}' is '{html.escape(top_candidate)}' (score {top_score:.2f})</strong>"
                                f"{boxed_preview_fb}"
                                "</div>"
                            )

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

        # samp_name: only validate per-row if the column exists
        if 'samp_name' in present_columns:
            samp = (row.get('samp_name') or '').strip()
            if not samp:
                errors.append(f"Row {i}: missing sample name ('samp_name').")

        # ref_start / ref_end numeric: only validate if both columns are present
        if 'ref_start' in present_columns and 'ref_end' in present_columns:
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

        # defect: only validate if column exists
        if 'defect' in present_columns:
            defect_val = (row.get('defect') or '').strip()
            if not defect_val:
                warnings.append(f"Row {i}: empty 'defect' field.")

        # boolean-like checks: only validate columns that exist
        for bool_col in ('is_defective', 'is_inverted'):
            if bool_col not in present_columns:
                continue
            val = (row.get(bool_col) or '').strip().lower()
            if val and val not in ('0', '1', 'true', 'false', 't', 'f'):
                warnings.append(
                    f"Row {i}: column '{bool_col}' has non-standard value '{html.escape(row.get(bool_col) or '')}'."
                    " Expected 0/1 or True/False."
                )

    return errors, warnings, suggestions


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
            f"<div style='border:1px solid #d9534f;padding:12px;background:#f8d7da;color:#721c24;'><h2>Problem reading your file</h2><p>{html.escape(read_err)}</p><p>Please make sure you uploaded a CSV file and that it is readable. If you opened the file in Excel or Google Sheets, try exporting/saving as CSV and upload that.</p></div>"
        )
        return website.generate_site()

    # Validate
    errors, warnings, suggestions = _validate_csv_text(csv_text)

    # Present validation results in plain, user-friendly language
    if errors:
        website.send("<h1 style='color:#a94442'>We couldn't create your plot</h1>")
        website.send("<p>There are problems in your file that prevent us from making the plot. Please fix the items below and try again.</p>")
        website.send("<p>If you are using a spreadsheet program (Excel, Numbers, Google Sheets): make sure the first row contains the column names and save/export as CSV before uploading.</p>")
        website.send(_make_box('What to fix', errors, '#a94442', '#f2dede', '#a94442'))
        if warnings:
            website.send(_make_box('Things to check', warnings, '#f0ad4e', '#fcf8e3', '#8a6d3b'))
        # If we have header suggestions (likely because required columns were missing), show them here too
        if suggestions:
            website.send("<h2 style='color:#31708f'>Suggested fixes for column names</h2>")
            website.send("<p style='background:#eef9ff;padding:8px;border-left:4px solid #31708f;'>Tip: To fix a column name, open your CSV or spreadsheet and change the name in the first row (the column headers). The suggestions below show likely corrections. Whitespace (extra spaces) is highlighted when present.</p>")
            for sug in suggestions:
                website.send(sug)
            website.send("<p>After making changes, save the file as CSV and upload it again.</p>")
        website.send("<p>Please fix these issues and try again. No plot was generated.</p>")
        return website.generate_site()

    if warnings:
        website.send("<h2 style='color:#8a6d3b'>We noticed some issues</h2>")
        website.send("<p>We could create the plot despite them, but these items below might have affected the result. Please check them and correct if needed.</p>")
        website.send(_make_box('Things to check', warnings, '#f0ad4e', '#fcf8e3', '#8a6d3b'))

    if suggestions:
        website.send("<h2 style='color:#31708f'>Suggested fixes for column names</h2>")
        website.send("<p style='background:#eef9ff;padding:8px;border-left:4px solid #31708f;'>Tip: To fix a column name, open your CSV or spreadsheet and change the name in the first row (the column headers). The suggestions below show likely corrections. Whitespace (extra spaces) is highlighted when present.</p>")
        for sug in suggestions:
            website.send(sug)
        website.send("<p>These suggestions are just that — suggestions. If you know your file is correct, you can continue.</p>")

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
    website.send("<img width='100%' src='/media/output.svg' alt='Output svg' />")
    # Add a centered, prominent download button so non-technical users can easily save the image
    website.send(
        "<div style='text-align:center;margin:16px 0;'>"
        "<a href='/media/output.svg' download='proviral_landscape.svg' "
        "style='display:inline-block;background:#31708f;color:#fff;padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:600;box-shadow:0 4px 10px rgba(0,0,0,0.12);'>"
        "Download"
        "</a>"
        "</div>"
    )

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

def _has_visible_whitespace(s: str) -> bool:
    """Return True if string has leading/trailing spaces or any tab characters."""
    if s is None:
        return False
    return (s != s.lstrip(' \t')) or (s != s.rstrip(' \t')) or ('\t' in s)


def _visible_whitespace_html(s: str) -> str:
    if s is None:
        s = ''

    rep = html.escape(s)
    rep = rep.replace(' ', "<span style='background:#fffbdd;color:#a94442;padding:0 1px;margin:0;'>·</span>")
    rep = rep.replace('\t', "<span style='background:#fffbdd;color:#a94442;padding:0 1px;margin:0;'>⇥</span>")
    return rep


def _boxed_column_preview(exp_html: str, found_html: str) -> str:
    """Return HTML showing 'Expected' and 'Found' labels with tight boxes around the
    provided HTML fragments (which are already escaped/highlighted). The boxes are
    rendered using a two-column CSS grid (fixed-width label column, auto value column)
    so the left edge of both boxed values always lines up exactly.
    """
    label_w = '80px'
    # box is tight to content; max-width prevents runaway long text, preserve monospace
    box_style = (
        "display:inline-block;border:1px solid #cfcfcf;padding:2px 2px;"
        "font-family:monospace;background:#fff;white-space:pre;max-width:70vw;"
        "overflow-wrap:break-word;"
    )
    container_style = (
        f"margin-top:6px;display:grid;grid-template-columns:{label_w} auto;"
        "column-gap:8px;row-gap:6px;align-items:start;"
    )

    return (
        f"<div style='{container_style}'>"
        # Expected row
        f"<div style='color:#666;font-size:smaller;'>Expected:</div>"
        f"<div style='justify-self:start;'><span style='{box_style}'>{exp_html}</span></div>"
        # Found row
        f"<div style='color:#666;font-size:smaller;'>Found:</div>"
        f"<div style='justify-self:start;'><span style='{box_style}'>{found_html}</span></div>"
        "</div>"
    )
