# Checked for Python3.7

# Notes:
# - When creating a file, make sure it's folder has enough permissions.
#

import re, cgi, os, sys
import datetime

# Add the path to util scripts.
sys.path.append( os.environ.get('BBLAB_UTIL_PATH', 'fail') ) 
import mailer
import math_utils
import web_output
from web_output import clean_html

OUT_PATH = os.path.dirname(os.path.realpath(__file__)) + "/output/"

def run(input_string, session_id, row_column, email_address_string):

	##### Create an instance of the site class for website creation.
	website = web_output.Site( "Results", web_output.SITE_BOXED )
	website.set_footer( 'go back to <a href="/django/wiki/">wiki</a>' )
	

	##### Process and Vailate Input

	
	# clean_html makes sure that users can't have their own html rendered.	
	
	input_string = math_utils.fix_line_endings( input_string )
	
	row_column = ("Column" if row_column == "2" else "Row")
	
	if input_string.find(',') == -1:
		website.send_error( "Could not find any ',' characters,", " did you format your input correctly?" )
		return website.generate_site()		

	row_id_list = [ row[:row.find(',')] for row in input_string.split('\n') if row.find(',') != -1 ]


	##### Create .csv file (for machine)
	
	
	header = " Sample ID, Sample well, Sample volume (ml), Dilution factor, Events to Acquire, Time Limit, Replicates, Autosave FCS 2.0 files, Mix Time (sec), Mix Speed (rpm),, General settings,\n";
	header += ", T1, 10.000000, 1.000000, 5000, 600, No, No, 3, High,,Assay Type, InCyte\n";
	header += ", T2, 10.000000, 1.000000, 5000, 600, No, No, 3, High,,Acquisition Order, by {}\n".format( row_column );
	header += ", T3, 10.000000, 1.000000, 5000, 600, No, No, 3, High,,Do Clean,Every 24 samples\n";
	header += ", T4, 10.000000, 1.000000, 5000, 600, No, No, 3, High,,Wash only capillary,Yes\n";
	header += ", T5, 10.000000, 1.000000, 5000, 600, No, No, 3, High,,Wash both capillary and mixer,Yes\n";
	header += ", T6, 10.000000, 1.000000, 5000, 600, No, No, 3, High,,Mixing,Yes\n";
	header += ", T7, 10.000000, 1.000000, 5000, 600, No, No, 3, High,,Cleaning Option,Clean and Rinse\n";
	header += ", T8, 10.000000, 1.000000, 5000, 600, No, No, 3, High,,Limit for high concentration warning (cells/uL),500\n";
	header += ", T9, 10.000000, 1.000000, 5000, 600, No, No, 3, High\n, T10, 10.000000, 1.000000, 5000, 600, No, No, 3, High\n";
	
	body = input_string  # js does the formatting for us.
	
	# Save a text copy of the file; to email.
	csv_file_text = header + body
	
	# Write to file.
	csv_filename = '{}.csv'.format( clean_html(session_id) )
	if os.path.realpath(OUT_PATH) == os.path.dirname(os.path.realpath(OUT_PATH+csv_filename)):
		if not os.path.isfile(OUT_PATH+csv_filename):
			with open(OUT_PATH+csv_filename, 'w') as csv_file:
				csv_file.write( csv_file_text )
			website.send( "Created .csv file." )
		else:
			website.send_error( "{} could not be added to the archive,".format(csv_filename), " a file already exists with the same name." )
	else:
		website.send_error("Improper Filename,", " make sure your filename does not include any invalid characters.")
		return website.generate_site()

	
	##### Create .html file.  (for person.)
	
	
	# All these lines of code format the text together.  ( likely not the best programming here... )
	table = 'table { border-width: 0 0 1px 1px; border-style:solid; }'
	td    = 'td { border-color: #600; border-width: 1px 1px 0 0; border-style: solid; margin: 0; padding: 4px; text-align:center; }'
	tr    = 'tr.even { background-color:#EEEEEE; } tr.odd { background-color:#FFFFFF }'
	dark  = 'td.dark { background-color:#E3E3E3; }'
	light = 'td.light { background-color:#FFFFFF; }'
	empty = 'td.empty {color:#999999; }'
	style = '<style type="text/css">{}</style>'.format(table + td + tr + dark + light + empty)
	head  = '<head>{}</head>'.format( style )
	
	column_dict_string = "ABCDEFGH"
	column_key = 0
	
	# Init table contents with the key.
	tr = ''
	for num in range(13):
		tr += ('<td>*</td>' if num == 0 else ('<td>{}</td>'.format(num)))
	tr = '<tr>{}</tr>'.format( tr )
	
	# Holds the contents of the entire table.
	table_contents = tr
	row_string = ''  # Holds the contents of each row.
	counter = 0
	for string in row_id_list:  # Loop through each id
		string = clean_html(string)
		if counter > 12:
			# Reset the row and add it to the table.
			table_contents += '<tr>{}</tr>'.format( row_string )
			row_string = ''  
			counter = 0
			column_key += 1
	
		if counter == 0:
			row_string += '<td class="light">{}</td>'.format( column_dict_string[column_key] )
			counter += 1	
			
		if string == "":  # Case: no id is at the current slot.
			row_string += '<td class="empty"><i>empty</i></td>'	
		elif ((counter+int(column_key > 3)) % 2) == 1:
			row_string += '<td class="dark">{}</td>'.format( string )	
		else:
			row_string += '<td class="light">{}</td>'.format( string )	
	
		counter += 1
	
	table_contents += '<tr>{}</tr>'.format( row_string )
	
	tbody = '<tbody>{}</tbody>'.format( table_contents  )
	table = '<table border="1">{}</table>'.format( tbody )
	date = '<h2>Date: {}</h2>'.format( str(datetime.datetime.now()).split(" ")[0] )
	titles = '<h1>GUAVA LAYOUT</h1>' + '<h2>Session ID: {}</h2>'.format( clean_html(session_id) ) + date
	body = '<body>{}{}</body>'.format( titles, table )
	
	html_text_main = "<html>{}{}</html>".format( head, body )  # This is the html string copy.
	
	# Write to file
	html_filename = "{}.html".format( clean_html(session_id) )
	if os.path.realpath(OUT_PATH) == os.path.dirname(os.path.realpath(OUT_PATH+html_filename)):
		if not os.path.isfile(OUT_PATH+html_filename):	
			with open(OUT_PATH+html_filename, 'w') as new_file:
				new_file.write( html_text_main )
			website.send( "Created .html file. <br>..." )
		else:
			website.send_error( "{} could not be added to the archive,".format(html_filename), " a file already exists with the same name." )
	else: 
		website.send_error("Improper Filename,", " make sure your filename does not include any invalid characters.")
		return website.generate_site()	
	

	##### Give user a link to the file directory.  ( Before the email )
	
	
	website.send( 'Your files have been generated.<br>' )
	web_address = "/django/tools/guava_layout/output/"
	website.send( '<a style="font-size: 1.5em;" href="{}">Go to file directory</a><br><br>'.format( web_address ) ) 
	
	
	##### Send email with the files in it.
	
	
	website.new_box()
	website.send( "<br>" )
	
	csv_file = mailer.create_file( session_id, 'csv', csv_file_text )
	html_file = mailer.create_file( session_id, 'html', html_text_main )
	
	# Add the body to the message and send it.
	end_end = "Note: all guava layout files can be found at https://bblab-hivresearchtools.ca/django/tools/guava_layout/output/"
	end_message = "This is an automatically generated email, please do not respond.\n\n" + end_end
	msg_body = "Session ID: {}\nThe included files ({} and {}) contain the requested formatting data. \n\n{}".format(session_id, csv_filename, html_filename, end_message)
	cc_address = "zbrumme@sfu.ca"
	
	if mailer.send_sfu_email("guava_layout", email_address_string, "GUAVA LAYOUT: {}".format(session_id), msg_body, [csv_file, html_file], [cc_address]) == 0:
		website.send( "An email has been sent to <b>{}</b> with a full table of results. <br>Make sure <b>{}</b> is spelled correctly.".format(email_address_string, email_address_string) )
	
	# Check if email is formatted correctly.  (Could be a slightly better check.)
	if not re.match(r"[^@]+@[^@]+\.[^@]+", email_address_string):
		website.send( "<br><br> Your email address (<b>{}</b>) is likely spelled incorrectly, please re-check its spelling.".format(email_address_string) )
	
	website.send( "<br>" )
	website.new_box()
	

	##### Archive any files that are older than 30 days.
	
	
	import filesys_utils
		
	archive_path = "{}archived_layouts/".format(OUT_PATH)
	print_string = filesys_utils.archive_in_dir(OUT_PATH, archive_path, 30)  # Move files older that 30 days from OUT_PATH to archive_path, 
	website.send(print_string + "<br>")	
	
	return website.generate_site()
