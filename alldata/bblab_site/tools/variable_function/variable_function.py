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

	
	##### Process Data


	normalized_data = normalizeNewlines(forminput)
	result = [x.split("\t") for x in normalized_data.split("\n") if x]
	unique_categories = set([inner for outer in result for inner in outer[:-1]])
	unique_categories = set([x for x in unique_categories if x])
	
	# Make sure all function values can be converted to float.
	try:
		for row in result:
			if float(row[-1]) >= 1 or float(row[-1]) <= 0:
				raise ValueError
	except ValueError:
		return(False, "<b><span style=\"color:red;\">Error:</span></b> make sure the VALUE at the end of each line is a decimal number in the range (0, 1)")
	
	
	##### Run Analysis


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
		<th>p-value</th></tr></thead><tbody>""")
		for category in unique_categories:
			positive = [float(x[-1]) for x in result if category in x[:-1]]
			pos_median = median(positive)
			negative = [float(x[-1]) for x in result if category not in x[:-1]]
			neg_median = median(negative)
			u, p = stats.mannwhitneyu(positive, negative)
			out_str += ("""<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>
				<td>{:.8f}</td></tr>""".format(category,len(positive),len(negative),pos_median,neg_median,p))
		
		out_str += ("</tbody></table></body></div>")
	
	# The "Download CSV" button was pressed
	else:
		is_download = True	
		
		# The following is to print csv style
		out_str += ("category,n-with,n-without,median-with,median-without,p-value\r\n")
		for category in unique_categories:
			positive = [float(x[-1]) for x in result if category in x[:-1]]
			pos_median = median(positive)
			negative = [float(x[-1]) for x in result if category not in x[:-1]]
			neg_median = median(negative)
			u, p = stats.mannwhitneyu(positive, negative)
			out_str += ("{},{},{},{},{},{}\r\n".format(category,len(positive),len(negative), pos_median, neg_median, p))
	
	return (is_download, out_str, "variable_function_output.csv")
