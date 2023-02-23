import sys
import os
sys.path.append(os.environ.get('BBLAB_UTIL_PATH', 'fail'))
import web_output
import mailer
from . import proviral_landscape_plot


def run(csv_data, analysis_id, email_address_string):
    # Create an instance of the site class for website creation.
    website = web_output.Site("Proviral Landscape Plot - Results", web_output.SITE_BOXED)
    website.set_footer('go back to <a href="/django/wiki/" >wiki</a>')

    # Get website input.
    with open('output.svg', 'w') as output_svg:
        proviral_landscape_plot.create_proviral_plot(csv_data, output_svg)

    website.send("<img src = 'output.svg' alt='Output svg'")

    # Send email
    # Create subject line
    subject_line = "Proviral Landscape Plot Results"
    if analysis_id:
        subject_line += " - {}".format(analysis_id)

    # Add the body to the message and send it.
    msg_body = (f"Test email for ID {analysis_id}")

    if mailer.send_sfu_email("proviral_landscape_plot", email_address_string, subject_line, msg_body) == 0:
        website.send(("An email has been sent to <b>{}</b> with a full table of results."
                      "<br>Make sure <b>{}</b> is spelled correctly.").format(email_address_string,
                                                                              email_address_string))

    return website.generate_site()
