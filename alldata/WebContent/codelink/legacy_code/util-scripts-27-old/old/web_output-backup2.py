import cgi

class Site:
	'''
	This class handles formatting a simple text output website with css using 
	the cgi module.
	'''

	def __init__(self, title="Website", is_debug_mode=False):
		'''
		Debug mode is for error detection.  It just means that it prints the string right after having it 
		passed to the function, instead of doing it all at once at the end of the script.
		'''
		self._site_title = title
		self._feed_contents = []
		self._is_debug_mode = is_debug_mode
		self._have_placed_header = False
		self._footer_text = "this is a website"

	def set_title(self, title):
		self._site_title = title
	
	# Footer is printed after the main feed. (under)
	def set_footer(self, footer_text):
		self._footer_text = footer_text
	
	def _print_header(self):
		print ( 'Content-type: text/html \n' )  # This is python 2.7 and 3.6 compatible.
		print ( '<html><head>' )
		print ( '<link rel="stylesheet" href="../python_dependencies/css/style.css"/>' )  # Css link.
		print ( '<title>{}</title>'.format( self._site_title ) )  # Title. 
		print ( '</head><body><div id="container">' )

	def generate_site(self):
		'''
		This function prints all code to the console which builds
		the website.  This should be called at the end of the script.
		'''
		if self._is_debug_mode == False:
			self._print_header()
		
		# Print all the strings in the feed_contents list.
		for string in self._feed_contents: 
			print ( string )

		print ( '</div></body>' )  # Complete the body and feed.
		print ( '<p id="footer">' + self._footer_text + '</p>' )
		print ( '</html>' )  # Complete the html output.

	
	def send_break(self):
		'''
		This function adds a break which separates the text before it from the text after it.
		'''
		if self._is_debug_mode == False:
			self._feed_contents += [ '<div class="break"></div><br>' ]
		else:
			if self._have_placed_header == False:
				self._have_placed_header = True 
				self._print_header()
			print ( "<br>--this will be a break--<br>" )

	def send(self, string):
		'''
		This function acts like the print command, it sends the
		string to the main section of the website to be outputed. (After the error and warning log.)
		'''
		if self._is_debug_mode == False:
			self._feed_contents += [string]
		else:
			if self._have_placed_header == False:
				self._have_placed_header = True 
				self._print_header()
			print ( string )
	
	
