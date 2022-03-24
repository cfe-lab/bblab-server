#!/lib/anaconda3/bin/python3.7

import sys
#sys.stderr = sys.stdout  # This is the godlike line of code! -> prints errors to cgi.

import re, cgi, sys

CGI_BIN_PATH = "/var/www/cgi-bin"
PKGS_PATH = "/lib/anaconda3/pkgs"

sys.path.append( "{}/depend/util_scripts/".format(CGI_BIN_PATH) ) 
import math_utils  # Does it use this?


##### Get website input.


# Get form data from the website.
form = cgi.FieldStorage()  
pvalue_string = form.getvalue("pValues")


##### Make sure data is acceptable (validate input) and process data.


def throw_error(string):
	print ( "Content-type: text/html\n" )
	print ( "<html><head><title>Results</title></head><body>" )
	print ( string )
	print ( "</body></html>" )

if pvalue_string == None:
	throw_error( "<b><r style=\"color: orange;\">Warning:</r> Could not find any characters,</b> is the input empty?<br>" )
	sys.exit(1)
elif pvalue_string.find('\n') == -1 and pvalue_string.find('\r') == -1:
	throw_error( "<b><r style=\"color: orange;\">Warning:</r> Could not find any 'newline' characters,</b> did you format your input correctly?<br>" )
	sys.exit(1)

# Convert pvalue list to float.
try: 
	pvalue_list = [ float(item) for item in pvalue_string.replace('\r', '\n').replace("\n\n", '\n').split('\n') if item != '' ]
except ValueError:
	throw_error( "<b><r style=\"color: red;\">Error:</r> Inputted data must be decimal numbers.</b> (pvalues) Is your input formatted correctly?<br>" )
	sys.exit(1)

	
##### Convert p-values into q-values using R script


sys.path.append( "{}/depend/operations/".format(CGI_BIN_PATH) )  # Add the path to this tool's operations module.
import op_qvalue

qvalues = op_qvalue.get_qvalues( pvalue_list )


##### Create an excel file to hold qvalue data


sys.path.append( "{}/depend/libraries/".format(CGI_BIN_PATH) )  # Add the path to openpyxl, (excel files.)
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


# This is pretty much pure magic.
x = "Content-type: application/octet-stream; charset=\"binary\""
x2 = "Content-Disposition: attachment; filename=\"{}.xlsx\"".format(XLSX_FILENAME)
x3 = "Content-Transfer-Encoding: binary\r\n\r\n"

sys.stdout.buffer.write( bytes(x+"\n"+x2+'\n'+x3, "utf-8")+file_text )
