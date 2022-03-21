# This is python 3.7 Compatible #

# This is used to check for errors in input and email addresses so far.


# I dunno if this is very important to have as util script....

import re

def is_field_empty(field_str, field_name, site):
	if field_str == "" or field_str == " " or field_str == "\n" or \
			field_str == "\r\n":
		site.send_error("{} is empty.".format(field_name))
	
def check_email(email_str, site):
	if email_str == "" or email_str == " ":
		site.send_error( "You didn't enter an email address.", " please enter an email address." )

	elif not re.match(r"[^@]+@[^@]+\.[^@]+", email_str):
		site.send_error( "Your email address (<em>{}</em>) is missing necessary characters,".format(email_str), \
				" please re-check its spelling." )

