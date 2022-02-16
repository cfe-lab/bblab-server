# This module is compatible with Python 3.7 #
import sys, os

from scipy import stats  # For the p value calculation function.

sys.path.append( os.environ.get('BBLAB_UTIL_PATH', 'fail') ) 
import sequence_utils
import math_utils

sys.path.append( os.environ.get('BBLAB_OP_PATH', 'fail') )
import op_qvalue

def get_output_matrix( protein_sequences, min_count):
	"""
	This function processes the inputted protein sequence data and outputs a 'matrix'
	containing all the data needed to construct the resulting excel file.

	depends on: qvalue, sequence_utils, math_utils, scipy, numpy. 
	"""

	##### Class and function definitions

	class ProteinData:
		'''
		This class holds the data for a single protein character in its column column.
		'''

		def __init__(self, char, decimal_list):
			self.protein_char = char
			self.decimal_list = decimal_list

		# This function returns how many times this protein characters appears by getting the data
		# from the decimal value list's length.
		def get_occurrances(self):
			return len(self.decimal_list)

	class ColumnData:
		'''
		This class holds the ProteinData for everything in this column (of the input data).
		'''
		
		# nw_protein_list is a list of ProteinData classes, while with_protein_data is just one.
		def __init__(self, column_pos, w_protein_dat, nw_protein_list):
			self.with_protein_data = w_protein_dat
			self.not_with_protein_data_list = nw_protein_list
			self.position = column_pos

		def get_with(self):
			return self.with_protein_data

		def get_not_with_list(self):
			return self.not_with_protein_data_list
	
		# This function gets all the decimal lists from not-with and combines them.
		def get_not_with_decimal_list(self):
			sum_decimal_list = []
			for data in self.not_with_protein_data_list:
				sum_decimal_list += data.decimal_list
			return sum_decimal_list

		# This function gets all the occurrance values from not-with and combines them into one number.
		def get_not_with_occurrances(self):
			sum_occurrance_count = 0
			for data in self.not_with_protein_data_list:
				sum_occurrance_count += data.get_occurrances()
			return sum_occurrance_count
	
	class ColumnOutput:
		'''
		ColumnOutput contains the information that will be formatted into a .xlsx file.
		'''
	
		def __init__(self, coord, with_amino, with_median, notwith_median, with_count, notwith_count, p_value, q_value):
			self.coord = coord
			self.w_amino = with_amino
			self.w_median = with_median
			self.nw_median = notwith_median
			self.w_count = with_count
			self.nw_count = notwith_count
			self.p_value = p_value
			self.q_value = q_value
	
		# This function formats all the information and returns it as a list. ( row )
		def get_formatted_row(self):
			return [ self.coord, self.w_amino, self.w_median, self.nw_median, self.w_count, self.nw_count, self.p_value, self.q_value ]


	# This function extracts and calculates the needed data from the ColumnData class.
	def _run_seq_test( column_data ):
		w_amino = column_data.get_with().protein_char  # Get Protein char for with.
	
		w_decimal_list = column_data.get_with().decimal_list  # Save the decimal list for later.
		w_median = math_utils.median( w_decimal_list )
	
		# Find the median of all not-with decimal values.
		nw_decimal_list = column_data.get_not_with_decimal_list()
		nw_median = math_utils.median( nw_decimal_list )
	
		w_count = column_data.get_with().get_occurrances()
	
		# Find the sum of all not-with occurance counts.
		nw_count = column_data.get_not_with_occurrances()
	
		p_value = math_utils.round_sf(stats.kruskal(w_decimal_list, nw_decimal_list)[1], 5)  # Use scipy to find the p-values.	
		
		# Put all this information into the ColumnOutput class.
		output_column = ColumnOutput( column_data.position+1, w_amino, w_median, nw_median, w_count, nw_count, p_value, -1)
	
		# Send the output column to the output matrix.
		output_matrix.append( output_column ) 

	##### Run tests on the given sequences. 

	sequence_length = len(protein_sequences[0][1])  # Init the length to be the length of the first protein sequence.
	output_matrix = []  # This matrix holds the data that will be added to the excel file.(and returned) This is a list of dictionaries, so... matrix?

	# Iterate over each item in the sequences.
	for column_index in range(sequence_length):
		# Create and fill a list that contains all proteins at the current position and their decimal value.
		codon_list = [] # -> [ (char, decimal), ... ]
		for seq_index in range(len(protein_sequences)):
			codon_list.append( (protein_sequences[seq_index][1][column_index], protein_sequences[seq_index][0]) )  # list of -> (character, decimal)
	
		# Count how many of each protein there is.
		data_dict = {}  # This is a dict of ProteinData classes with char as the key. -> { char : ProteinData }
		valid_characters = 0  # This holds how many valid characters were counted.  ( For checking validity. )
		for tup in codon_list:
			char = tup[0]
			decimal = float(tup[1])

			if not char in sequence_utils.protein_mixture_list:  # Make sure that invalid characters (mixtures) are not counted in this step.
				valid_characters += 1

				if char in data_dict:
					data_dict[ char ].decimal_list += [ decimal ]  # Populate the decimal list.
				else:
					data_dict[ char ] = ProteinData( char, [decimal] )  # Init the ProteinData class.
	
		# Find the proteins that have an occurance value higher than minCount.
		if len(data_dict) > 1:  # Case: there are at least two different proteins in this column.
			valid_data = [] 

			for data in data_dict.values():	
				# Check if current char is a vaild group.
				if data.get_occurrances() >= min_count and valid_characters - data.get_occurrances() >= min_count:
					valid_data += [ data ]
		else:
			continue  # Case: all characters equal, ignore.

		if len(valid_data) <= 0:
			continue  # Case: no valid data groups.
	
	
		# Do analysis
		for index in range( 0, len(valid_data) ):
			# Put with and not with into the same container.
			data_dict.pop( valid_data[index].protein_char )  # Temp pop.

			column_data = ColumnData( column_index, valid_data[index], data_dict.values() )
			_run_seq_test( column_data )  # Run test on the data.
	
			data_dict[valid_data[index].protein_char] = valid_data[index]  # Add the item back to the dictionary. 
	
	# Generate qvalues using the entire list of pvalues.	
	pvalue_list = [] 
	for item in output_matrix:
		pvalue_list.append( item.get_formatted_row()[6] ) 

	qvalue_list = op_qvalue.get_qvalues( pvalue_list )  # Get q values using the r script.
	for matrix_index in range(0, len(output_matrix)):
		output_matrix[matrix_index].q_value = qvalue_list[matrix_index]

	return output_matrix
