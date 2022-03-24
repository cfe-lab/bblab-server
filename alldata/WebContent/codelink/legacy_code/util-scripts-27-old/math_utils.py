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

# This is a really poor algorithm.  Try and fix it! ... or maybe not ... don't break anything ... please.
def round_to_sig_figs(number, sig_figs):
	'''
	Rounds a (small [designed for less than 10 decimals] ) number to a certain amount of significant figures.
	ex. 4.56765 rounded to 3 significant figures is 4.56
		0.08894 rounded to 3 significant figures is 0.0889
	This function is only meant for stripping decimals.  If used with larger numbers, results may vary.
	'''
	num_string = str(number)
	num_len = len(num_string)
	end_zeros = 0
	start_zeros = 0
	for index in range(num_len-1, 0, -1):  # End zeros
		if num_string[index] == '0' or num_string[index] == '.':
			num_string = num_string[:-1]
		else:
			break;
	for index in range(0, num_len-1): # Start zeros
		if num_string[index] == '0':
			start_zeros += 1
		elif num_string[index] != '.':
			break;
	if start_zeros > 0:
		length = len(num_string.replace('.', '')) - 1
	else:
		length = len(num_string.replace('.', '')) - 0

	end_off = (len(num_string.replace('.', ''))-start_zeros)-sig_figs
	
	return round(float(num_string), length-end_off)

