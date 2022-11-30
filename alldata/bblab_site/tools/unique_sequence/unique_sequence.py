# Checked for Python3.7

import sys, re, os

# Add the path to util scripts. 
sys.path.append( os.environ.get('BBLAB_UTIL_PATH', 'fail') )
import sequence_utils
import mailer

# Add the path to openpyxl.
sys.path.append( os.environ.get('BBLAB_LIB_PATH', 'fail') )
from openpyxl import Workbook
import openpyxl
import web_output

def run(fasta_data, desc_string, email_address_string):

	##### Create an instance of the site class for website creation.	
	website = web_output.Site("Unique Sequence - Results", web_output.SITE_BOXED)	
	website.set_footer( 'go back to <a href="/django/wiki/" >wiki</a>' )


	##### Get website input.
	
	analysis_id = desc_string
	input_field_text = [e+'\n' for e in str( fasta_data ).replace('\r', '\n').replace('\n\n', '\n').split('\n') if e]
	
	try:
		# Convert file to a list of tuples.
		fasta_list = sequence_utils.convert_fasta( input_field_text )
	except Exception:
		website.send_error("Failed to read fasta data,", " is something formatted wrong?")
		return website.generate_site()		

	# Convert the dna sequences to uppercase.
	index = 0
	for tup in fasta_list:
		fasta_list[index] = (tup[0], tup[1].upper())
		index += 1

	
	##### Validate Input


	# Check if all sequences contain valid characters.
	send_error = False
	char_messages = ""

	for tup in fasta_list:
		char_pos = 0
		for char in tup[1]:
			if (char in sequence_utils.valid_protein_character_list) == False:
				send_error = True
				char_messages += "<br><b>{}</b> was found at position {} of {}.".format(char, char_pos, tup[0])  # Report any invalid characters.
			char_pos += 1
 
	# Print error message.
	if send_error == True:
		website.send_error( "Some invalid characters have been found,", " please remove them to run the analysis." + char_messages )
		return website.generate_site()


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
	
	
	##### Find most repetitions.
	
	
	most_DNA_repetitions = 0  # This holds the most repetitions for any sequence.
	for key, value in list( dna_sequences_dict.items() ):
		repetitions = len(value)
	
		# Check for largest repetitions value.
		if repetitions > most_DNA_repetitions:
			most_DNA_repetitions = repetitions
	
	most_amino_acid_repetitions = 0  # This holds the most repetitions for any sequence.
	for key, value in list( amino_acid_sequences_dict.items() ):
		repetitions = len(value)
	
		# Check for largest repetitions value.
		if repetitions > most_amino_acid_repetitions:
			most_amino_acid_repetitions = repetitions 
	
	
	##### Create an xlsx file.
	
	
	XLSX_FILENAME = "{}_unique_sequence_data".format( analysis_id )
	
	wb = Workbook()  # Create a new workbook.
	ws = wb.active  # Create a new page. (worksheet [ws])
	ws.title = "DNA Sequences"
	
	# Create key row information.
	ws.append( ["Number", "Frequency", "Sequence", "Sequence Length", "Unique Sequence ID"] + ["Duplicate Sequence ID" for i in range(1, most_DNA_repetitions)] )
	
	# Create data row information.
	index = 0
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

	
	##### Send an email with the xlsx file in it.
	
	
	# Add the body to the message and send it.
	end_message = "This is an automatically generated email, please do not respond."
	msg_body = ( "The included .xlsx file ({}.xlsx) contains the requested {}. \n\n"
		     "Description: {} \n\n{}".format(XLSX_FILENAME, "unique sequence finder data", desc_string, end_message) )
	
	if mailer.send_sfu_email("unique_sequence_finder", email_address_string, "Unique Sequence Finder Results {}".format( desc_string ), msg_body, [xlsx_file]) == 0:
		website.send(( "An email has been sent to <b>{}</b> with a full table of results." 
			       "<br>Make sure <b>{}</b> is spelled correctly." ).format(email_address_string, email_address_string))
	
	
	##### Check if email is formatted correctly.
	
	
	if not re.match(r"[^@]+@[^@]+\.[^@]+", email_address_string):
		website.send( "<br>Your email address (<b>{}</b>) is likely spelled incorrectly, please re-check its spelling.".format(email_address_string) )

	return website.generate_site()	
