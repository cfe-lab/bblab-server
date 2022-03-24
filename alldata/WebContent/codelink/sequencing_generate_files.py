#!/lib/anaconda3/bin/python3.7

# Notes:
# - When creating a file, make sure it's folder has enough permissions.
#
 
# Start html output.
print ( "Content-type: text/html \n" )
print ( "<html><head>" )
print ( "<title>Results</title>" ) 
print ( "</head><body>" )

import re, cgi, os, sys
import datetime

CGI_BIN_PATH = "/var/www/cgi-bin/"

# Add the path to util scripts.
sys.path.append( "{}/depend/util_scripts/".format(CGI_BIN_PATH) )
import mailer
import math_utils

OUT_PATH = "/alldata/WebContent/tools/sequencing_layout/output/"  # This is the path to the output directory. (The free write directory.)


##### Get website input.


form = cgi.FieldStorage()  # Get form data from the website.

input_string = math_utils.fix_line_endings( str(form.getvalue("manualFields")) )
username = str(form.getvalue("userName"))
plate_id = str(form.getvalue("plateID"))
email_address_string = str(form.getvalue("emailAddress"))
machine = str(form.getvalue("sequencingMachine"))

	
##### Process and Vailate Input


if input_string.find('+') == -1:
	print ( "<br><b><r style=\"color: red;\">Error:</r> Could not find any '+' characters,</b> did you format your input correctly?" )
	sys.exit(0)

input_list = input_string.split('\n')
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
plt_filename = "{}.plt".format(plate_id)
with open(OUT_PATH+plt_filename, 'w') as new_file:
	new_file.write( plt_file_text ) 

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
		
	for tuple in input_matrix[row_num]:  # Loop through each item.
		sample_string += '<td>{}</td>'.format( tuple[0] )
		primer_string += '<td>{}</td>'.format( tuple[1] )

	dual_row_string = '<tr class="even">{}</tr> <tr class="odd">{}</tr>'.format( sample_string + '<td></td>', primer_string + '<td></td>')
	table_contents += dual_row_string

tr = ''
for num in range(13):
	tr += ('<td>*</td>' if num == 0 else ('<td>{}</td>'.format(num)))
tr = '<tr>{}</tr>'.format( tr )

tbody = '<tbody>{}{}</tbody>'.format( tr, table_contents  )
table = '<table border="1">{}</table>'.format( tbody )
titles = '<h1>SEQUENCING LAYOUT</h1>' + '<h2>Plate ID: {}, User name: {}</h2>'.format( plate_id, username )
body = '<body>{}{}</body>'.format( titles, table )

html_text_main = "<html>{}{}</html>".format( head, body )  # This is the html string copy.

# Write to file
html_filename = "{}.html".format(plate_id)
with open(OUT_PATH+html_filename, 'w') as new_file:
	new_file.write( html_text_main ) 


##### Give user a link to the file directory.  ( Before the email )


print ( 'Your files have been generated.<br>' )
web_address = "https://bblab-hivresearchtools.ca/tools/sequencing_layout/output/"
print ( '<a style="font-size: 1.5em;" href="{}">Go to file directory</a><br><br>'.format(web_address) )


##### Send email with the files in it.


# Draw a line above the message.
print ( "--"*35 )
print ( "<br><br>" )

plt_file = mailer.create_file( plate_id, 'plt', plt_file_text )
html_file = mailer.create_file( plate_id, 'html', html_text_main )

# Add the body to the message and send it.
end_message = "This is an automatically generated email, please do not respond."
msg_body = "The included files ({} and {}) contain the requested formatting data. \n\n{}".format(plt_filename, html_filename, end_message)
cc_address = "zbrumme@sfu.ca"

if mailer.send_sfu_email("plate_layout_designer", email_address_string, "PLATE LAYOUT: {}".format(plate_id), msg_body, [plt_file, html_file], [cc_address]) == 0:
	print ( "An email has been sent to <b>{}</b> with a full table of results. <br>Make sure <b>{}</b> is spelled correctly.".format(email_address_string, email_address_string) )

# Check if email is formatted correctly.
if not re.match(r"[^@]+@[^@]+\.[^@]+", email_address_string):
	print ( "<br><br> Your email address (<b>{}</b>) is likely spelled incorrectly, please re-check its spelling.".format(email_address_string) )

# Draw a line under the message.
print ( "<br><br>" )
print ( "--"*35 )


##### Archive any files that are older than 30 days.


import filesys_utils

archive_path = "{}Archived_Layouts/".format(OUT_PATH)
filesys_utils.archive_in_dir(OUT_PATH, archive_path, 30)  # Archive files in OUT_PATH, older than 30 days. 

print ( '<br>' )
print ( "--"*35 )  # Draw a line.
print ( '<br>' )

print ( "<br> python version: " + sys.version)  # Print version number.
print ( "</body></html>" )  # Complete the html output.
