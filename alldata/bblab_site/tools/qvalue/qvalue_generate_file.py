# Checked for Python3.7

import re, sys, os
from django.http import HttpResponse

sys.path.append( os.environ.get('BBLAB_UTIL_PATH', 'fail') ) 
import math_utils 

def run(pvalue_string):
	##### Make sure data is acceptable (validate input) and process data.
	
	
	def throw_error(string):
		out_str += ( "<html><head><title>Results</title></head><body>" )
		out_str += ( string )
		out_str += ( "</body></html>" )
		return out_str

	if pvalue_string == None:
		return (False, throw_error( "<b><r style=\"color: orange;\">Warning:</r> Could not find any characters,</b> is the input empty?<br>" ))
	elif pvalue_string.find('\n') == -1 and pvalue_string.find('\r') == -1:
		return (False, throw_error( "<b><r style=\"color: orange;\">Warning:</r> Could not find any 'newline' characters,</b> did you format your input correctly?<br>" ))
	
	# Convert pvalue list to float.
	try: 
		pvalue_list = [ float(item) for item in pvalue_string.replace('\r', '\n').replace("\n\n", '\n').split('\n') if item != '' ]
	except ValueError:
		return (False, throw_error( "<b><r style=\"color: red;\">Error:</r> Inputted data must be decimal numbers.</b> (pvalues) Is your input formatted correctly?<br>" ))
		
			
	##### Convert p-values into q-values using R script
	
	
	sys.path.append( os.environ.get('BBLAB_OP_PATH', 'fail') )  # Add the path to this tool's operations module.
	import op_qvalue
	
	qvalues = op_qvalue.get_qvalues( pvalue_list )
	
	
	##### Create an excel file to hold qvalue data
	
	
	sys.path.append( os.environ.get('BBLAB_LIB_PATH', 'fail') )  # Add the path to openpyxl, (excel files.)
	from openpyxl import Workbook
	import openpyxl
	
	XLSX_FILENAME = "q-values"
	
	wb = Workbook()
	ws = wb.active
	ws.title = "Data"
	
	ws.append( ["p-values", "q-values"] )
	
	for i in range(len(qvalues)):
		ws.append( [pvalue_list[i], qvalues[i]] )
	
	file_text = openpyxl.writer.excel.save_virtual_workbook(wb)
	
	
	##### Push file to the browser.

	
	response = HttpResponse(file_text, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
	response['Content-Disposition'] = 'inline; filename={}.xlsx'.format(XLSX_FILENAME)
	return (True, response)

	# I am so proud of this garbage but I don't need it anymore so I'm saving it.
	'''
	# This is pretty much pure magic.
	x = "Content-type: application/octet-stream; charset=\"binary\""
	x2 = "Content-Disposition: attachment; filename=\"{}.xlsx\"".format(XLSX_FILENAME)
	x3 = "Content-Transfer-Encoding: binary\r\n\r\n"
	
	sys.stdout.buffer.write( bytes(x+"\n"+x2+'\n'+x3, "utf-8")+file_text )
	'''
