## Checked for 3.7 ##
import math

def median(lst):
	'''
	When passed a list of numbers returns the median average of the group.
	'''
	lst = sorted(lst)
	length = len(lst)
	half_length = int(length/2)

	if length % 2 == 0:  # Case: even length.
		return (lst[half_length] + lst[half_length-1])/2  
	else:
		return lst[half_length]  # Gets the center element.

def is_string_int(string):
	'''
	Determines if a string can be converted into an int.
	'''
	try: 
		int(string)
		return True
	except ValueError:
		return False

def find_matches(string, char):
	'''
	Will return a list of the indices of "string" in which "char" occur.	
	'''
	return [i for i, letter in enumerate(string) if letter == char]

# Fixed it! Use round_sf in the future.
def round_to_sig_figs(number, sig_figs):
	return round_sf(number, sig_figs)

# sf -> significant figures
def round_sf(num, sf):
	'''
	Rounds a number to a certain amount of significant figures.
	ex. 4.56765 rounded to 3 significant figures is 4.56
	    0.08894 rounded to 3 significant figures is 0.0889

	This algorithm was the first google result, why couldn't I find it before...
	
	Negative numbers will fail b/c log10(x).
	'''
	if num < 0: 
		raise ValueError("This function doesn't accept negative numbers.")
	return round(num, -int(math.floor(math.log10(num))) + (sf - 1))

def fix_line_endings(string):
	'''
	This handles \n, \r, and \r\n. and converts them all into \n. 
	'''
	return string.replace('\r', '\n').replace('\n\n', '\n')
	

