#!/lib/anaconda3/bin/python3.7

# Start html output.
print ( "Content-type: text/html\n" )
print ( "<html><head>" )
print ( "<title>Results</title>" ) 
print ( "</head><body>" )

import sys
print ( sys.version + '<br>' )

import re
import cgi
import smtplib
from email.mime.text import MIMEText

CGI_BIN_PATH = "/var/www/cgi-bin"

# Add the path to util scripts. 
sys.path.append( "{}/depend/util_scripts/".format(CGI_BIN_PATH) )
import sequence_utils
import mailer

# Add the path to openpyxl.
sys.path.append( "{}/depend/libraries/".format(CGI_BIN_PATH) )
from openpyxl import Workbook
import openpyxl


##### Get website input.


form = cgi.FieldStorage()  # Get form data from the website.

file_item = form['file']  # Get the file item

# Check if the file was submitted to the form.
if file_item.filename:
	# Read the file's text.
	input_field_text = [e+'\n' for e in str( file_item.value.decode("utf-8") ).replace('\r', '\n').replace('\n\n', '\n').split('\n') if e]
	
else:
	# Get user input string and convert it into a list of lines.
	input_field_text = [e+'\n' for e in str( form.getvalue("fastaInputArea") ).replace('\r', '\n').split('\n') if e]

email_address_string = str(form.getvalue("emailAddress"))

# Convert file to a list of tuples.
fasta_list = sequence_utils.convert_fasta( input_field_text )

# Convert the dna sequences to uppercase.
index = 0
for tuple in fasta_list:
	fasta_list[index] = (tuple[0], tuple[1].upper())
	index += 1


##### Fill the DNA sequence dictionary.


# key = DNA sequence, value = list of dna sequence names.
dna_sequences_dict = {}  # store all unique dna sequences and their name.

# Iterate through all dna sequences and find the unique sequences.
for tuple in fasta_list:
    is_sequence_unique = True

    # Iterate through all the current unique dna sequences.
    for key in dna_sequences_dict:
        if tuple[1] == key:  # Case: current tuple is not unique.
            dna_sequences_dict[key].append(tuple[0])  # Add the name for the current dna sequence to the list.

            # Processing of the current tuple is complete, sequence is not unique.
            is_sequence_unique = False
            continue

    # Case: current tuple was found to be unique.
    if is_sequence_unique == True:
        sequence_index = len(dna_sequences_dict) + 1  # Find the sequence's id. (or index)
        dna_sequences_dict[ tuple[1] ] = [ tuple[0] ]  # Add a dna sequence to the dict.


##### Fill the Amino Acid sequence dictionary.


# key = amino acid sequence, value = list of amino acid sequence names.
amino_acid_sequences_dict = {}  # store all unique dna sequences and their name.

# Iterate through all dna sequences, convert them to amino acids, then find the unique sequences.
for tuple in fasta_list:
	is_sequence_unique = True

	amino_acid_sequence = sequence_utils.translate_nuc( tuple[1], 0 )  # Convert the dna part of the sequence into an amino acid sequence.

	# Iterate through all the current unique amino acid sequences.
	for key in amino_acid_sequences_dict:
		if amino_acid_sequence == key:  # Case: current tuple is not unique.
			amino_acid_sequences_dict[key].append(tuple[0])  # Add the name for the current amino acid sequence to the list.

			# Processing of the current tuple is complete, sequence is not unique.
			is_sequence_unique = False
			continue

	# Case: current tuple was found to be unique.
	if is_sequence_unique == True:
		sequence_index = len(amino_acid_sequences_dict) + 1  # Find the sequence's id. (or index)
		amino_acid_sequences_dict[ amino_acid_sequence ] = [ tuple[0] ]  # Add a amino acid sequence to the dict and add the id at [0].


##### Output the immediate results to the webpage.


most_DNA_repetitions = 0  # This holds the most repetitions for any sequence.

# Format and print console output.
for key, value in list( dna_sequences_dict.items() ):
	#index += 1
	#sequence_id = index  # The sequence number.
	repetitions = len(value)
	#identical_sequence_list = value  # This list holds all the names of identical sequences.
	##dna_sequence = key  # The key is the actual dna string.
		
	##print ( "Sequence {} is repeated {} times : {} <br>".format(sequence_id, repetitions, identical_sequence_list) )

	# Check for largest repetitions value.
	if repetitions > most_DNA_repetitions:
		most_DNA_repetitions = repetitions

most_amino_acid_repetitions = 0  # This holds the most repetitions for any sequence.

# Format and print console output.
for key, value in list( amino_acid_sequences_dict.items() ):
	#index += 1
	#sequence_id = index  # The sequence number.
	repetitions = len(value)
	#identical_sequence_list = value  # This list holds all the names of identical sequences.
	##amino_acid_sequence = key  # The key is the actual amino acid string.
	
	##print ( "Sequence {} is repeated {} times : {} <br>".format(sequence_id, repetitions, identical_sequence_list) )

	# Check for largest repetitions value.
	if repetitions > most_amino_acid_repetitions:
		most_amino_acid_repetitions = repetitions 


##### Create an xlsx file.


XLSX_FILENAME = "unique_sequence_data"

wb = Workbook()  # Create a new workbook.
ws = wb.active  # Create a new page. (worksheet [ws])
ws.title = "DNA Sequences"

# Create key row information.
ws.append( ["Number", "Frequency", "Sequence", "Sequence Length", "Unique Sequence ID"] + ["Duplicate Sequence ID" for i in range(1, most_DNA_repetitions)] )

# Create data row information.
index = 0
##for key, value in list( sorted(dna_sequences_dict.items(), key=lambda (k,v): (-len(v),k)) ):
for key, value in list( sorted( dna_sequences_dict.items(), key=lambda t: (-len(t[1]), t[0]) ) ):
	index += 1
	sequence_id = index  # The sequence number.
	repetitions = len(value)
	identical_sequence_list = value  # This list holds all the names of identical sequences.
	dna_sequence = key  # The key is the actual dna string.
	sequence_length = len(dna_sequence)
	
	ws.append( [sequence_id, repetitions, dna_sequence, sequence_length] + identical_sequence_list )

ws2 = wb.create_sheet("Mysheet")
ws2.title = "Amino Acid Sequences"

# Create key row information.
ws2.append( ["Number", "Frequency", "Sequence", "Sequence Length", "Unique Sequence ID"] + ["Duplicate Sequence ID" for i in range(1, most_amino_acid_repetitions)] )

# Create data row information.
index = 0
#for key, value in list( sorted(amino_acid_sequences_dict.items(), key=lambda k,v: (-len(v),k)) ):
for key, value in list( sorted(amino_acid_sequences_dict.items(), key=lambda t: (-len(t[1]), t[0])) ):
	index += 1
	sequence_id = index  # The sequence number.
	repetitions = len(value)
	identical_sequence_list = value  # This list holds all the names of identical sequences.
	amino_acid_sequence = key  # The key is the actual amino acid string.
	sequence_length = len(amino_acid_sequence)
	
	ws2.append( [sequence_id, repetitions, amino_acid_sequence, sequence_length] + identical_sequence_list )

# Save a string version of the excel workbook and send it to the file builder.
file_text = openpyxl.writer.excel.save_virtual_workbook(wb)
xlsx_file = mailer.create_file( XLSX_FILENAME, 'xlsx', file_text )

# Draw a line above the message.
print ( "--"*35 )
print ( "<br><br>" )


##### Send an email with the xlsx file in it.


# Add the body to the message and send it.
end_message = "This is an automatically generated email, please do not respond."
msg_body = "The included .xlsx file ({}.xlsx) contains the requested sequence data. \n\n{}".format(XLSX_FILENAME, end_message)

if mailer.send_sfu_email("unique_sequence_finder", email_address_string, "Unique Sequence Finder Results", msg_body, [xlsx_file]) == 0:
	print ( "An email has been sent to <b>{}</b> with a full table of results. <br>Make sure <b>{}</b> is spelled correctly.".format(email_address_string, email_address_string) )


##### Check if email is formatted correctly.


if not re.match(r"[^@]+@[^@]+\.[^@]+", email_address_string):
	print ( "<br><br> Your email address (<b>{}</b>) is likely spelled incorrectly, please re-check its spelling.".format(email_address_string) )

print ( "</body></html>" )  # Complete the html output.
