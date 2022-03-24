# Checked for Python3.7

# Notes:
# - When creating a file, make sure it's folder has enough permissions.
#

import re, os, sys
import datetime

# Add the path to util scripts.
sys.path.append( os.environ.get('BBLAB_UTIL_PATH', 'fail') ) 
import mailer
import math_utils
import web_output
import filesys_utils
from web_output import clean_html

OUT_PATH = os.path.dirname(os.path.realpath(__file__)) + "/output/"  # This is the path to the output directory. (The free write directory.)

def run(input_string, username, plate_id, email_address_string, machine):
	
	##### Create an instance of the site class for website creation.
	website = web_output.Site( "Results", web_output.SITE_BOXED )
	website.set_footer( 'go back to <a href="/django/wiki/">wiki</a>' )


	##### Process and Vailate Input


	input_string = math_utils.fix_line_endings( input_string )

	if input_string.find('+') == -1:
		website.send_error( "Could not find any '+' characters,", " did you format your input correctly?" )
		return website.generate_site()

	input_list = input_string.strip('\n').split('\n')
	#input_list.pop()  # This is an evil line I thought i already fixed this bug... 
	input_matrix = [ [] for x in range(8) ]  # This variable is for the html file. type -> [ [ (sample, primer), ... ], ... ]
	column_counter = 0
	for string in input_list:
		if string == '':
			continue  # This is for the case of 1 or multiple trailing newline characters that get removed.
		sample, primer = string.split('+')
		input_matrix[column_counter] += [ (sample, primer) ]
	
		if column_counter >= 7:
			column_counter = 0
		else:
			column_counter += 1


	##### Create .plt file


	# Make sure '\n' is ok here and not '\r' or '\r\n'
	header_title = "Container Name\tPlate ID\tDescription\tContainerType\tAppType\tOwner\tOperator\tPlateSealing\tSchedulingPref\n"  
	header_data = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( plate_id, plate_id, "IMPORT API", "96-Well", "Regular", username, username, "Septa", "1234" )
	bottom_header_title = "AppServer\tAppInstance\t\t\t\t\t\t\t\n"
	bottom_header_data = "SequencingAnalysis\t\t\t\t\t\t\t\t\n"
	
	body_key = "Well\tSample Name\tComment\tResults Group 1\tInstrument Protocol 1\tAnalysis Protocol 1\n"
	
	body = ""  # Holds all the rows of data.
	
	column_dict_string = "ABCDEFGH"
	column_key = 0
	row_value = 1
	for string in input_list:
		# Build each row.
		row_string = "{}\t{}\t{}\t{}\t{}\t".format( str(column_dict_string[column_key])+str(row_value), string, "SFU", "CFE_Results_Group", "CFE_DEFAULT" )
			
		if machine == "B":  # (sfu)
			row_string += "POP7_BDV3\t\t\t\n" 
		elif machine == "C":  # (st.pauls)
			row_string += "3730BDTv3-KB-DeNovo_v5.2\t\t\t\n"
	
		body += row_string
		
		# Increment the Well column value (and letter.).
		if column_key >= 7:
			row_value += 1
			column_key = 0
		else:
			column_key += 1

	# Save a text copy of the file to email.  # [:-1] is omitting the last character (a '\n') becasue the last line doesn't need a '\n'.
	plt_file_text = header_title + header_data + bottom_header_title + bottom_header_data + body_key + body[:-1] 
	
	# Write to file
	plt_filename = "{}.plt".format( clean_html(plate_id) )
	
	# This should protect from random directory filewriting.  TODO: check this!	
	if os.path.realpath(OUT_PATH) == os.path.dirname(os.path.realpath(OUT_PATH+plt_filename)):
		if not os.path.isfile(OUT_PATH+plt_filename):
			with open(OUT_PATH+plt_filename, 'w') as new_file:
				new_file.write( plt_file_text )
		else:
			website.send_error("{} could not be added to the archive,".format(plt_filename), " a file already exists with the same name.")
	else:
		website.send_error("Improper Filename,", " make sure your filename does not include any invalid characters.")
		return website.generate_site()

	
	##### Create .html file


	# All these lines of code format the text together.  ( likely not the best programming here... )
	table = 'table { border-width: 0 0 1px 1px; border-style:solid; }'
	td    = 'td { border-color: #600; border-width: 1px 1px 0 0; border-style: solid; margin: 0; padding: 4px; text-align:center; }'
	tr    = 'tr.even { background-color:#EEEEEE; } tr.odd { background-color:#FFFFFF }'
	style = '<style type="text/css">{}</style>'.format(table + td + tr)
	head  = '<head>{}</head>'.format( style )
		
	table_contents = ''
	for row_num in range(8):  # Loop through each row
		sample_string = '<td>{}</td>'.format( column_dict_string[row_num] )
		primer_string = '<td>&nbsp;</td>'
				
		for tup in input_matrix[row_num]:  # Loop through each item.
			sample_string += '<td>{}</td>'.format( clean_html(tup[0]) )
			primer_string += '<td>{}</td>'.format( clean_html(tup[1]) )
	
		dual_row_string = '<tr class="even">{}</tr> <tr class="odd">{}</tr>'.format( sample_string + '<td></td>', primer_string + '<td></td>')
		table_contents += dual_row_string
	
	tr = ''
	for num in range(13):
		tr += ('<td>*</td>' if num == 0 else ('<td>{}</td>'.format(num)))
	tr = '<tr>{}</tr>'.format( tr )
	
	tbody = '<tbody>{}{}</tbody>'.format( tr, table_contents  )
	table = '<table border="1">{}</table>'.format( tbody )
	titles = '<h1>SEQUENCING LAYOUT</h1>' + '<h2>Plate ID: {}, User name: {}</h2>'.format( clean_html(plate_id), clean_html(username) )
	body = '<body>{}{}</body>'.format( titles, table )
	
	html_text_main = "<html>{}{}</html>".format( head, body )  # This is the html string copy.
	
	html_filename = "{}.html".format( clean_html(plate_id) )

	if os.path.realpath(OUT_PATH) == os.path.dirname(os.path.realpath(OUT_PATH+html_filename)):		
		if not os.path.isfile(OUT_PATH+html_filename):
			# Write to file
			with open(OUT_PATH+html_filename, 'w') as new_file:
				new_file.write( html_text_main )
		else:
			website.send_error("{} could not be added to the archive,".format(html_filename), " a file already exists with the same name.")

	else:
		website.send_error("Improper Filename,", " make sure your filename does not include any invalid characters.")
		return website.generate_site()

	
	##### Give user a link to the file directory.  ( Before the email )


	website.send( 'Your files have been generated.<br>' )
	web_address = '/django/tools/sequencing_layout/output/'
	website.send( '<a style="font-size: 1.5em;" href="{}">Go to file directory</a><br><br>'.format(web_address) )


	##### Send email with the files in it.


	website.new_box()
	website.send( "<br>" )
	
	plt_file = mailer.create_file( plate_id, 'plt', plt_file_text )
	html_file = mailer.create_file( plate_id, 'html', html_text_main )
	
	# Add the body to the message and send it.
	end_message = "This is an automatically generated email, please do not respond."
	msg_body = "The included files ({} and {}) contain the requested formatting data. \n\n{}".format(plt_filename, html_filename, end_message)
	cc_address = "zbrumme@sfu.ca"
	
	if mailer.send_sfu_email("plate_layout_designer", email_address_string, "PLATE LAYOUT: {}".format(plate_id), msg_body, [plt_file, html_file], [cc_address]) == 0:
		website.send( "An email has been sent to <b>{}</b> with a full table of results. <br>Make sure <b>{}</b> is spelled correctly.".format(email_address_string, email_address_string) )
	
	# Check if email is formatted correctly.
	if not re.match(r"[^@]+@[^@]+\.[^@]+", email_address_string):
		website.send( "<br><br> Your email address (<b>{}</b>) is likely spelled incorrectly, please re-check its spelling.".format(email_address_string) )
	
	website.send( "<br>" )
	website.new_box()
	
	
	##### Archive any files that are older than 30 days.
	
	
	archive_path = "{}archived_layouts/".format(OUT_PATH)
	print_string = filesys_utils.archive_in_dir(OUT_PATH, archive_path, 30)  # Archive files in OUT_PATH, older than 30 days. 
	website.send( print_string + "<br>" )	
	
	return website.generate_site()  # This returns the website string.
		
