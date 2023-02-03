# Checked for 3.7
from scipy import stats
import cgi, sys, re, os

"""EXAMPLE OF VALID INPUT
A01\tA02\tB07\tB15\tC07\tC08\t0.1
A02\tA02\tB07\tB51\tC02\tC05\t0.2
A01\tA03\tB07\tB30\tC05\tC08\t0.3
"""
sys.path.append( os.environ.get('BBLAB_UTIL_PATH', 'fail') )
from math_utils import round_sf

def run(forminput, isCsv):

	out_str = ""

	##### Function Definitions


	def median(input_list):
		if input_list:
			input_list.sort()
			if(len(input_list) % 2 == 1):
				return input_list[len(input_list)//2]
			else:
				return round_sf((input_list[(len(input_list)-1)//2] + input_list[(len(input_list)+1)//2]) / 2.0, 15)
		else:
			return "N/A"
	
	def normalizeNewlines(string):
		return re.sub(r'(\r\n|\r|\n)', '\n', string)

	# Sort categories alphanumerically, with non-alphanumerics as delimeters
	# tailored for HLA types (i.e., "A02:01" < "A12:01:15G" < "A12:03:01")
	# adapted from https://nedbatchelder.com/blog/200712/human_sorting.html
	def alphanum_sort(categories):
		convert = lambda text: int(text) if text.isdigit() else text.lower()
		alphanum_key = lambda k: [ convert(c) for c in re.split('([0-9]+)', k) ]
		return sorted(categories, key=alphanum_key)

	
	##### Process Data


	normalized_data = normalizeNewlines(forminput)
	result = [x.split("\t") for x in normalized_data.split("\n") if x]
	unique_categories = set([inner for outer in result for inner in outer[:-1]])
	unique_categories = set([x for x in unique_categories if x])
	unique_categories = alphanum_sort(unique_categories)
	
	# Make sure all function values can be converted to float.
	try:
		samp_vals = set()
		for row in result:
			samp_val = row[-1]
			try:
				float(samp_val)
			except:
				raise ValueError("make sure the VALUE at the end of each line is a decimal number")
			samp_vals.add(samp_val)
		if len(samp_vals) == 1:
			raise ValueError("the VALUES at the end of each line are identical")
	except ValueError as e:
		return(False, f"<b><span style=\"color:red;\">Error:</span></b> {e}.")
	
	
	##### Run Analysis

	# Note: this is our override of SciPy's _mwu_choose_method
	#
	# This functions identically to _mwu_choose_method in SciPy 1.7.3, 
	# although it assumes x,y are (1-D) Python lists, not NumPy arrays.
	#
	# We use this to report whether thie MWU test was performed with 
	# 'asymptotic' or 'exact' p-values, and stabilize our rules
	# in the event that a newer version of SciPy changes these rules,
	# or removes this internal method.
	def mwu_choose_method(x, y):
		# if both inputs are large, asymptotic is OK
		if len(x) > 8 and len(y) > 8:
			return "asymptotic"
		# if there are any ties, asymptotic is preferred
		if len(x + y) != len(set(x + y)):
			return "asymptotic"
		return "exact"	

	def mannwhitneyu_category(result, category):
		pos = [float(x[-1]) for x in result if category in x[:-1]]
		pos_median = median(pos)
		neg = [float(x[-1]) for x in result if category not in x[:-1]]
		neg_median = median(neg)
		mwu_method = mwu_choose_method(pos, neg)
		_, p = stats.mannwhitneyu(pos, neg, alternative='two-sided', method=mwu_method)
		return [len(pos), len(neg), pos_median, neg_median, p, mwu_method]

	try:
		# If the button clicked was not the "Download CSV" button then output HTML
		if not isCsv:
			### Regular Analysis
			is_download = False
			out_str += ("""{% load static %}<html><head>
			<link rel="stylesheet" href="{% static "/jquery/themes/blue/style.css" %}">
			<link rel="stylesheet" href="{% static "/vfa_css/style.css" %}">
			<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
			<script src="{% static "/jquery/jquery.tablesorter.js" %}"></script>
			<script src="{% static "/jquery/myscript.js" %}"></script>
			</head><body><div class="container">\n""")
			
			# The following is to print html
			out_str += ("<table id='myTable' class='tablesorter'>")
			out_str += ("""<thead><tr class="header"><th>category</th><th>n-with</th>
			<th>n-without</th><th>median-with</th><th>median-without</th>
			<th>p-value</th><th>p-value-method</th></tr></thead><tbody>""")
			for category in unique_categories:
				output = mannwhitneyu_category(result, category)
				out_str += "<tr><td>" + "</td><td>".join(str(v) for v in [category, *output]) + "</td></tr>"
			out_str += ("</tbody></table></body></div>")
		
		# The "Download CSV" button was pressed
		else:
			is_download = True	
			
			# The following is to print csv style
			out_str += ("category,n-with,n-without,median-with,median-without,p-value,p-value-method\r\n")
			for category in unique_categories:
				output = mannwhitneyu_category(result, category)
				out_str += ",".join(str(v) for v in [category, *output]) + "\r\n"
		
		return (is_download, out_str, "variable_function_output.csv")
	except ValueError as e:
		return(False, f"""<b><span style=\"color:red;\">Error:</span></b> statistical test encountered an error with the given input. <br/>
						Common issues are that the input data contains unique categories in each column, <br/>
						or that not all sample values are identical. <br/> <br/>
						Error message: {e}""")