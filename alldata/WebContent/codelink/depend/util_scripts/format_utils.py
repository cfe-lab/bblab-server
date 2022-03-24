# TODO: just remove this?

def format_list(list, has_end_period=True):
	'''
	This function formats a list by turning it into a string with proper
	english grammer that lists of all the items in it. 
	This function returns a string.
	'''
	out_str = ""
	for item in list:
		out_str += str(item) + ", "
	
	return out_str[:-2]+('.'*has_end_period) 
	
