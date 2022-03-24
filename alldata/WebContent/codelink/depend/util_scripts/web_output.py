import cgi

#TODO: implement these two styles.
SITE_PLAIN = 0
SITE_BOXED = 1

class Site:
	'''
	This class handles formatting a simple text output feed website with css using the cgi module.

	The text feed is separated into sections with an area for errors and warnings at 
	the top of the page.  (and functions to send text to each of them.)
	'''

	def __init__(self, title="Website", site_style=SITE_BOXED, is_debug_mode=False):
		'''
		Debug mode is for error detection.  It just means that it prints the string right after having it 
		passed to the function, instead of doing it all at once at the end of the script.
		'''
		self._is_debug_mode = is_debug_mode
		self._have_placed_header = False #AKA: allready 'printed' header to cgi output

		self._site_title = title
		self._box_list = [ "" ]  # Inits with one box.
				
		self._errors = ""	
		self._warnings = ""
		self._style = site_style 	

	
		self._footer_text = "this is a website"
	
	def set_title(self, title):
		self._site_title = title
	
	# Footer is printed after the main feed. (under)
	def set_footer(self, footer_text):
		self._footer_text = footer_text
	
	def _print_header(self):
		print ( 'Content-type: text/html \n' )  # This is python 2.7 and 3.7 compatible.
		print ( '<html><head>' )
		print ( '<link rel="stylesheet" href="https://bblab-hivresearchtools.ca/codelink/depend/css/style.css"/>' )  # Css link.
		print ( '<title>{}</title>'.format( self._site_title ) )  # Title. 
		print ( '</head><body><div id="container">' )

	def generate_site(self):
		'''
		This function prints all code to the console which builds
		the website.  This should be called at the end of the script.
		
		Note: If in debug mode, only the footer is printed.
		'''
		
		if not self._is_debug_mode:
			self._print_header()

			# Print errors first.
			if self._errors != "":
				print('<div class="box"><br>{}<br></div>'.format(self._errors))
	
			# Print warnings second.
			if self._warnings != "":
				print('<div class="box"><br>{}<br></div>'.format(self._warnings))
	
			# Print all the strings in the feed_contents list.
			for contents in self._box_list: 
				print ( '<div class="box"><br>{}<br></div>'.format(contents) )
		
		print ( '</div></body>' )  # Complete the body and feed.
		print ( '<p id="footer">' + self._footer_text + '</p>' )
		print ( '</html>' )  # Complete the html output.
	
	def new_box(self):
		'''
		This function sends any text after it to the next box down the screen.		
		'''
		if self._is_debug_mode:
			if self._have_placed_header == False:
				self._have_placed_header = True 
				self._print_header()
			print ( '<br>---- NEXT BOX ----<br>' )
		else:
			self._box_list.append( "" )  # Add a new string to box list.  (Each string is the contents of a new box.)
				

	def send(self, string):
		'''
		This function acts like the print command, it sends the
		string to the main section of the website to be outputed. (After the error and warning log.)
		'''
		if self._is_debug_mode:
			if self._have_placed_header == False:
				self._have_placed_header = True 
				self._print_header()
			print ( string )
		else:
			# Add the string to the bottom most element of the box_list.  (Add to the bottom most box)
			self._box_list[ len(self._box_list)-1 ] += string + "<br>" 
	
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

		if self._is_debug_mode:
			if self._have_placed_header == False:
				self._have_placed_header = True 
				self._print_header()
			print ( '<br>' + error_string + '<br>' )	
		
		# Even when Debug mode, the error list must be filled so that has_error functions.
		self._errors += error_string + '<br>'

	def send_warning(self, bold, notbold=""):
		'''
		This function adds text to the warning box at the top of the feed. (under errors)
		
		bold 	-> The string that will be the beginning, bolded section of the warning message.
		notbold	-> The string that will be the ending, not bolded section of the warning message.
		
		Note: This function will format and add 'Warning:' to the string before displaying.
		Only include the actual error "message". 
		'''
		warning_string = '<b><r style="color: orange">Warning: </r>{}</b>{}'.format(bold, notbold)

		if self._is_debug_mode:
			if self._have_placed_header == False:
				self._have_placed_header = True 
				self._print_header()
			print ( '<br>' + warning_string + '<br>' )	
		
		# Even when Debug mode, the warning list must be filled so that has_warning functions.
		self._warnings += warning_string + '<br>'


	
