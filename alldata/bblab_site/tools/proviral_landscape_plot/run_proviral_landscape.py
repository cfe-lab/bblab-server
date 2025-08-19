import sys
import os
sys.path.append(os.environ.get('BBLAB_UTIL_PATH', 'fail'))
import web_output
import mailer
import json
from pathlib import Path
from . import proviral_landscape_plot


def run(csv_data, analysis_id, email_address_string):
    # Create an instance of the site class for website creation.
    website = web_output.Site("Proviral Landscape Plot - Results", web_output.SITE_BOXED)
    website.set_footer('go back to <a href="/django/wiki/" >wiki</a>')

    # Get website input.
    output_svg = '/alldata/bblab_site/media/output.svg'
    proviral_landscape_plot.create_proviral_plot(csv_data, output_svg)

    website.send("<img width='100%' src='/media/output.svg' alt='Output svg'")

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
    svg_content = Path(output_svg).read_text()
    plot_file = mailer.create_file( short_description, 'svg', svg_content )

    #
    # Actual send
    #
    if mailer.send_sfu_email("proviral_landscape_plot", email_address_string, subject_line, msg_body, [plot_file]) == 0:
        website.send(("An email has been sent to <b>{}</b> with your image."
                      "<br>Make sure <b>{}</b> is spelled correctly.").format(email_address_string,
                                                                              email_address_string))

    return website.generate_site()
