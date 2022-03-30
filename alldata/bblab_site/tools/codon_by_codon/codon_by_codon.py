# Checked for python 3.7

import re, sys, os

from depend.libraries.openpyxl import Workbook
from depend.libraries import openpyxl
from depend.libraries.openpyxl.writer.excel import save_virtual_workbook
from depend.util_scripts import sequence_utils, math_utils, mailer, web_output, test_utils
from depend.operations import op_codon_by_codon

def run(protein_in, min_count, desc_string, email_address_string):
	# Instance the cgi output class
	site = web_output.Site("codon by codon output", web_output.SITE_BOXED)	
	site.set_footer( 'go back to <a href="/django/wiki/">wiki</a>' )  


	##### Get website input.

			
	# Assign form data to variables.
	protein_in = protein_in.replace('\r', '\n').replace("\n\n", '\n').replace(' ', '')
	protein_sequences = [ tuple(e.split('\t')) for e in protein_in.split('\n') ]  # Turn this into a list of tuples. -> (decimal_value, protein_sequence)
	
	analysis_id = desc_string


	##### Make sure data is acceptable (validate data) and raise any warnings.

	
	if not math_utils.is_string_int(min_count):
		site.send_error( "Min count needs to be an integer;", " consider removing decimals or changing the value." )
	else:
		min_count = int(min_count)
	
	test_utils.is_field_empty(protein_in, "Main Input", site)
	test_utils.check_email(email_address_string, site)
	
	if site.has_error():
		site.send( "Analysis has been stopped." )
		return site.generate_site()
	
	try:
		# Check if all sequences are the correct length and find said length.
		sequence_length = len(protein_sequences[0][1])  # Init the length to be the length of the first protein sequence.
		for tup in protein_sequences:
			if len(tup[1]) != sequence_length:
				site.send_error( "All sequences are not the same length,", " please re-check their formatting." )
				return site.generate_site()	
	
	except IndexError: # This is triggered if random characters are in the main input (b/c list is not proper size)
		site.send_error( "Main Input is not formatted correctly,", " data cannot be read" )	
		site.send( "Analysis has been stopped." )
		return site.generate_site()
	
	# Check if all sequences contain valid characters.
	send_error = False
	char_messages = ""
	row_number = 0
	
	for tup in protein_sequences:
		row_number += 1	
		index = 0
		for char in tup[1]:
			if (char in sequence_utils.valid_protein_character_list) == False:
				send_error = True
				char_messages += "<br><b>{}</b> was found at position {} of row {}.".format(char, index, row_number)  # Report any invalid characters.
			index += 1
	
	# Print error message.
	if send_error == True:
		site.send_error( "Some invalid characters have been found,", " please remove them to run the analysis." + char_messages )	
		return site.generate_site()
	
	# Gives a warning if the sequence contains mixture characters.
	found_warning = False
	for tup in protein_sequences:
		if found_warning == True:  # This is the exit condition.
			break
		
		for char in tup[1]:
			if (char in sequence_utils.protein_mixture_list) == True:
				found_warning = True
				site.send_warning( "Some mixture characters (X and/or -) have been found in this analysis and will be ignored." )
				break		
	
	
	##### Run codon by codon analysis from its operation module.
		
	
	output_matrix = op_codon_by_codon.get_output_matrix(protein_sequences, min_count)	
		
	
	##### Create an xlsx file.
	
	
	XLSX_FILENAME = "{}_codon_by_codon".format( analysis_id )
	
	wb = Workbook()  # Create a new workbook.
	ws = wb.active  # Create a new page. (worksheet [ws])
	ws.title = "Data"  # Page title
	
	# Create the title row information (key).
	ws.append( ["Coord", "Amino", "Median(With)", "Median(Without)", "N(With)", "N(Without)", "Kruskal-wallis p", "q-value"] )
	
	# Add rows to the document.
	for item in sorted( output_matrix, key=lambda x: x.p_value ):
		ws.append( item.get_formatted_row() )
	
	# Save a string version of the excel workbook and send it to the file builder.
	file_text = save_virtual_workbook(wb)
	xlsx_file = mailer.create_file( XLSX_FILENAME, 'xlsx', file_text )
	
	
	##### Send an email with the xlsx file in it.
	
	
	# Add the body to the message and send it.
	end_message = "This is an automatically generated email, please do not respond."
	msg_body = ( "The included .xlsx file ({}.xlsx) contains the requested {}. \n\n"
		     "Analysis description: {} \n\n{}".format(XLSX_FILENAME, "codon analysis data", desc_string, end_message) )
	
	if mailer.send_sfu_email("codon_analysis", email_address_string, "Codon by codon analysis: {}".format( desc_string ), msg_body, [xlsx_file]) == 0:
		site.send ( "An email has been sent to <b>{}</b> with a full table of results. <br>Make sure <b>{}</b> is spelled correctly.".format(email_address_string, email_address_string) )
	
	return site.generate_site()
