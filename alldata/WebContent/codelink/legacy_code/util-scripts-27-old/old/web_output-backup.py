import cgi

class Site:
	'''
	This class handles formatting a simple text output website with css using 
	the cgi module.
	'''

	def __init__(self, title="Website", is_debug_mode=True):
		'''
		Debug mode is for error detection.  It just means that it prints the string right after having it 
		passed to the function, instead of doing it all at once at the end of the script.
		'''
		self._site_title = title
		self._str_contents = ""
		self._is_debug_mode = is_debug_mode
		self._have_placed_header = False

	def set_title(self, title):
		self._site_title = title
	
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
		print ( self._str_contents )  # Website contents.	
		print ( '</div></body></html>' )  # Complete the html output.

	def send(self, string):
		'''
		This function acts like the print command, it sends the
		string to the website to be outputed.
		'''
		if self._is_debug_mode == False:
			self._str_contents += string
		else:
			if self._have_placed_header == False:
				self._have_placed_header = True 
				self._print_header()
			print ( string )
	
	
