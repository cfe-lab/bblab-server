import cgi

## Changes: (while migrating to django)
## - Removed debug mode
## - Returns html as string instead of printing.

#TODO: implement these two styles.
SITE_PLAIN = 0
SITE_BOXED = 1


# Function is in two places so that is can be imported directly, even for non-direct web output 
# instances (like a file that gets written to disk, then read from another script.)
def clean_html(string):
	'''
	This function returns a string with any html tags, like the potentially dangerout "<script></script>",
	converted into html escapes, and thus rendered as plaintext.
	'''	
	return string.replace('<', "&lt;").replace('>', "&gt;")


class Site:
	'''
	This class handles formatting a simple text output feed website with css using the cgi module.

	The text feed is separated into sections with an area for errors and warnings at
	the top of the page.  (and functions to send text to each of them.)
	'''

	def __init__(self, title="Website", site_style=SITE_BOXED):
		self._site_title = title
		self._box_list = [ "" ]  # Inits with one box.

		self._errors = ""
		self._warnings = ""
		self._style = site_style


		self._footer_text = "this is a website"
		self._html = ""

	def set_title(self, title):
		self._site_title = title

	# Footer is printed after the main feed. (under)
	def set_footer(self, footer_text):
		self._footer_text = footer_text

	def _print_header(self):
		self._html += '{% load static %}\n<html><head>'
		self._html += '<link rel="stylesheet" href="{% static "wo_style.css" %}"/>' # Django static file integration.
		self._html += '<title>{}</title>'.format( self._site_title )  # Site Title
		self._html += '</head><body><div id="container">'

	def generate_site(self):
		'''
		This function prints all code to the console which builds
		the website.  This should be called at the end of the script.
		'''

		self._print_header()

		# Print errors first.
		if self._errors != "":
			self._html += '<div class="box"><br>{}<br></div>'.format(self._errors)

		# Print warnings second.
		if self._warnings != "":
			self._html += '<div class="box"><br>{}<br></div>'.format(self._warnings)
			
		if self._warnings == "" and self._errors == "":
			self._html += '<div class="box"><em><br>analysis executed successfully<br></em><br></div>'

		# Print all the strings in the feed_contents list.
		for contents in self._box_list:
			self._html += '<div class="box"><br>{}<br></div>'.format(contents)

		# Complete tags
		self._html += '</div></body>'
		self._html += '<p id="footer">' + self._footer_text + '</p>'
		self._html += '</html>'
		return self._html

	def new_box(self):
		'''
		This function sends any text after it to the next box down the screen.
		'''
		self._box_list.append( "" )  # Add a new string to box list.  (Each string is the contents of a new box.)


	def send(self, string):
		'''
		This function acts like the print command, it sends the
		string to the main section of the website to be outputed. (After the error and warning log.)
		
		WARNING: this function does not sanatize input, html will be rendered. Remember to clean user input so they
		cannot perform cross-site-scripting attacks.
		'''
		# Add the string to the bottom most element of the box_list.  (Add to the bottom most box)
		self._box_list[ len(self._box_list)-1 ] += string + "<br>"
	
	def clean_html(self, string):
		'''
		This function returns a string with any html tags, like the potentially dangerout "<script></script>",
		converted into html escapes, and thus rendered as plaintext.
		'''	
		return clean_html(string)

	def has_error(self):
		return False if self._errors=="" else True

	def has_warning(self):
		return False if self._warnings=="" else True

	def send_error(self, bold, notbold=""):
		'''
		This function adds text to the error box at the top of the feed.

		bold 	-> The string that will be the beginning, bolded section of the error message.
		notbold	-> The string that will be the ending, not bolded section of the error message.

		i.e.:
			input: (bold, notbold) -> ("sequence not divisible by 3,", " consider rechecking sequences.")
			output: <b><r style="color: red">ERROR:</r> sequence not divisible by 3,</b> consider rechecking sequences.

		Note: This function will format and add 'Error:' to the string before displaying.
		Only include the actual error "message."
		'''
		error_string = '<b><r style="color: red">Error: </r>{}</b>{}'.format(bold, notbold)

		# Even when Debug mode, the error list must be filled so that has_error functions.
		self._errors += error_string + '<br>'

	def send_warning(self, bold, notbold=""):
		'''
		This function adds text to the warning box at the top of the feed. (under errors)
		
		Works same as errors but yellow.
		'''
		warning_string = '<b><r style="color: orange">Warning: </r>{}</b>{}'.format(bold, notbold)

		# Even when Debug mode, the warning list must be filled so that has_warning functions.
		self._warnings += warning_string + '<br>'
