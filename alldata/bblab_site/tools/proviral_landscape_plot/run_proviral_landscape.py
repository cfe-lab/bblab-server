import sys
import os
sys.path.append(os.environ.get('BBLAB_UTIL_PATH', 'fail'))
import web_output
import mailer
import json
from pathlib import Path
import io
import csv
import html
import traceback


def run(csv_data, analysis_id, email_address_string):
    # Create an instance of the site class for website creation.
    website = web_output.Site("Proviral Landscape Plot - Results", web_output.SITE_BOXED)
    website.set_footer('go back to <a href="/django/wiki/" >wiki</a>')

    # Read the incoming CSV data into memory (always produce a seekable stream)
    try:
        if hasattr(csv_data, 'read'):
            raw = csv_data.read()
            # if bytes, decode
            if isinstance(raw, bytes):
                raw = raw.decode('utf8')
            csv_text = raw
        else:
            # assume a path-like string
            csv_text = Path(csv_data).read_text(encoding='utf8')
    except Exception as exc:
        msg = f"Could not read input CSV: {html.escape(str(exc))}"
        website.send(f"<div style='border:1px solid #d9534f;padding:12px;background:#f8d7da;color:#721c24;'><h2>Critical error</h2><p>{msg}</p></div>")
        return website.generate_site()

    # Create a CSV reader for validation
    stream = io.StringIO(csv_text)
    try:
        reader = csv.DictReader(stream)
    except Exception as exc:
        website.send(f"<div style='border:1px solid #d9534f;padding:12px;background:#f8d7da;color:#721c24;'><h2>Invalid CSV</h2><p>Failed to parse CSV header: {html.escape(str(exc))}</p></div>")
        return website.generate_site()

    headers = reader.fieldnames or []
    required_columns = ['samp_name', 'ref_start', 'ref_end', 'defect', 'is_defective', 'is_inverted']
    errors = []
    warnings = []

    # Check for presence of required columns
    for col in required_columns:
        if col not in headers:
            errors.append(f"Missing required column: '{col}'")

    if not headers:
        errors.append("No CSV header found or file is empty.")

    # Inspect a limited number of rows to validate types/values
    stream.seek(0)
    reader = csv.DictReader(stream)
    max_inspect_rows = 2000
    inspected = 0
    seen_defects = set()
    for i, row in enumerate(reader, start=1):
        if inspected >= max_inspect_rows:
            break
        inspected += 1
        # allow completely empty rows
        if not any((v and v.strip() for v in row.values())):
            continue
        # samp_name
        samp = (row.get('samp_name') or '').strip()
        if not samp:
            errors.append(f"Row {i}: missing sample name ('samp_name').")
        # ref_start / ref_end numeric
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
        # defect
        defect_val = (row.get('defect') or '').strip()
        if not defect_val:
            warnings.append(f"Row {i}: empty 'defect' field.")
        else:
            seen_defects.add(defect_val)
        # boolean-like checks
        for bool_col in ('is_defective', 'is_inverted'):
            val = (row.get(bool_col) or '').strip().lower()
            if val and val not in ('0', '1', 'true', 'false', 't', 'f'):
                warnings.append(f"Row {i}: column '{bool_col}' has non-standard value '{html.escape(row.get(bool_col) or '')}'. Expected 0/1 or True/False.")

    # Build styled messages
    def make_box(title, items, border, bg, text_color):
        if not items:
            return ''
        lis = ''.join(f"<li>{html.escape(s)}</li>" for s in items)
        return f"<div style='border:1px solid {border};padding:12px;background:{bg};color:{text_color};margin:8px 0;'><strong>{html.escape(title)} ({len(items)})</strong><ul style='margin:6px 0 0 18px;padding:0;'>{lis}</ul></div>"

    # If critical errors found, display them and bail out BEFORE importing plot module
    if errors:
        website.send("<h1 style='color:#a94442'>Input validation failed</h1>")
        website.send(make_box('Errors', errors, '#a94442', '#f2dede', '#a94442'))
        if warnings:
            website.send(make_box('Warnings', warnings, '#f0ad4e', '#fcf8e3', '#8a6d3b'))
        website.send("<p>Please correct the CSV file and try again. No plot was generated.</p>")
        return website.generate_site()

    # If only warnings, show them but continue
    if warnings:
        website.send("<h2 style='color:#8a6d3b'>Validation warnings</h2>")
        website.send(make_box('Warnings', warnings, '#f0ad4e', '#fcf8e3', '#8a6d3b'))
        website.send("<p>The plot will be generated but some rows may be unexpected. Inspect the warnings above.</p>")
    else:
        website.send("<div style='border:1px solid #5cb85c;padding:10px;background:#dff0d8;color:#3c763d;'><strong>Validation passed</strong> — generating plot.</div>")

    # Safe point: import plotting module only after validation succeeded
    try:
        from . import proviral_landscape_plot
    except Exception as exc:
        website.send("<h2 style='color:#a94442'>Internal error</h2>")
        website.send(f"<div style='border:1px solid #a94442;padding:12px;background:#f2dede;color:#a94442;'><p>Failed to import plotting module: {html.escape(str(exc))}</p></div>")
        website.send(f"<pre style='background:#fff;padding:8px;border:1px solid #eee;'>{html.escape(traceback.format_exc())}</pre>")
        return website.generate_site()

    # Generate the plot using a fresh, seekable stream constructed from the validated text
    input_stream = io.StringIO(csv_text)
    try:
        output_svg = '/alldata/bblab_site/media/output.svg'
        proviral_landscape_plot.create_proviral_plot(input_stream, output_svg)
    except Exception as exc:
        website.send("<h2 style='color:#a94442'>Plot generation failed</h2>")
        website.send(f"<div style='border:1px solid #a94442;padding:12px;background:#f2dede;color:#a94442;'><p>Unexpected error while creating plot: {html.escape(str(exc))}</p></div>")
        website.send(f"<pre style='background:#fff;padding:8px;border:1px solid #eee;'>{html.escape(traceback.format_exc())}</pre>")
        return website.generate_site()

    # Send image to website
    website.send("<img width='100%' src='/media/output.svg' alt='Output svg' />")

    short_description = analysis_id
    if len(short_description) > 30:
        short_description = short_description[:30] + "..."

    # Send email
    # Create subject line
    subject_line = "Proviral Landscape Plot Results"
    if short_description:
        subject_line += " - {}".format(short_description)

    # Add the body to the message and send it.
    quoted_description = json.dumps(short_description)
    msg_body = f"Your landscape plot, described as {quoted_description}, is ready. See the attachment."

    #
    # Prepare the file
    #
    svg_content = Path(output_svg).read_text(encoding='utf8')
    plot_file = mailer.create_file( short_description, 'svg', svg_content )

    #
    # Actual send
    #
    if mailer.send_sfu_email("proviral_landscape_plot", email_address_string, subject_line, msg_body, [plot_file]) == 0:
        website.send(("An email has been sent to <b>{}</b> with your image.""<br>Make sure <b>{}</b> is spelled correctly.").format(email_address_string,
                                                                                                                      email_address_string))

    return website.generate_site()
