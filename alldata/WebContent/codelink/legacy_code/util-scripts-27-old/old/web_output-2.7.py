import cgi

class Site:
	'''
	This class handles formatting a simple text output feed website with css using the cgi module.

	The text feed is separated into boxes with an area for errors and warnings at 
	the top of the page.  (and functions to send text to each of them.)
	'''

	def __init__(self, title="Website", is_debug_mode=False):
		'''
		Debug mode is for error detection.  It just means that it prints the string right after having it 
		passed to the function, instead of doing it all at once at the end of the script.
		'''
		self._is_debug_mode = is_debug_mode
		self._have_placed_header = False

		self._site_title = title
		self._box_list = [ "" ]  # Inits with one box.
				
		self._error_list = []	
		self._warning_list = []	

	
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
		
		Note: If in debug mode, only the footer is printed.
		'''
		
		if self._is_debug_mode == False:
			self._print_header()
			
			# Print all the strings in the feed_contents list.
			for box_contents in self._box_list: 
				print ( '<div class="box">{}</div>'.format(box_contents) )
		
		print ( '</div></body>' )  # Complete the body and feed.
		print ( '<p id="footer">' + self._footer_text + '</p>' )
		print ( '</html>' )  # Complete the html output.

	
	def new_box(self):
		'''
		This function sends any text after it to the next box down the screen.		
		'''
		if self._is_debug_mode == True:
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
		if self._is_debug_mode == True:
			if self._have_placed_header == False:
				self._have_placed_header = True 
				self._print_header()
			print ( string )
		else:
			self._box_list[ len(self._box_list)-1 ] += string  # Add the string to the bottom most element of the box_list.  (Add to the bottom most box)

	# TODO: finish this and warnings.
	def add_to_error(self, bold, notbold):
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
		error_string = '<b><r style="color: red">ERROR: </r>{}</b>{}'.format(bold, notbold)

		if self._is_debug_mode == True:
			if self._have_placed_header == False:
				self._have_placed_header = True 
				self._print_header()
			print ( '<br>' + error_string + '<br>' )
		
		else:
			self._error_list.append( error_string ) 
	
