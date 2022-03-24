#!/lib/anaconda3/bin/python3.7

# Start html output.
print ( "Content-type: text/html \n" )  # Note: This is 2.7 and 3.6  compatible.
print ( "<html><head>" )
print ( "<title>Results</title>" ) 
print ( "</head><body>" )

import re, cgi, sys

CGI_BIN_PATH = "/var/www/cgi-bin"
PKGS_PATH = "/lib/anaconda3/pkgs"

sys.path.append( "{}/scipy-0.14.0-np19py27_0/lib/python3.7/site-packages/".format(PKGS_PATH) )  # Add the path to scipy.
sys.path.append( "{}/numpy-base-1.9.0-py27_0/lib/python3.7/site-packages/".format(PKGS_PATH) )  # Add the path to numpy.
sys.path.append( "{}/depend/libraries/".format(CGI_BIN_PATH) )  # Add path to qvalue.
import qvalue  # qvalue uses scipy and numpy.  

sys.path.append( "{}/depend/util_scripts/".format(CGI_BIN_PATH) ) 
import math_utils  # Does it use this?


##### Get website input.


# Get form data from the website.
form = cgi.FieldStorage()  
pvalue_string = form.getvalue("pValues")


##### Make sure data is acceptable (validate input) and process data.


if pvalue_string.find('\n') == -1 and pvalue_string.find('\r') == -1:
	print ( "<b><r style=\"color: orange;\">Warning:</r> Could not find any 'newline' characters,</b> did you format your input correctly?<br>" )

if pvalue_string.find('.') == -1:
	print ( "<b><r style=\"color: orange;\">Warning:</r> Could not find any '.' characters,</b> did you format your input correctly?<br>" )

# Convert pvalue list to float.:0

try: 
	pvalue_list = [ float(item) for item in pvalue_string.replace('\r', '\n').replace("\n\n", '\n').split('\n') if item != '' ]
except ValueError:
	print ( "<b><r style=\"color: red;\">Error:</r> Inputted data must be decimal numbers.</b> (pvalues) Is your input formatted correctly?<br>" )
	sys.exit(1)

from numpy import array
numpy_pvalue_array = array( pvalue_list )

	
##### Convert p-values into q-values using the module.


#import qvalueold  # qvalue uses scipy and numpy.  
import scipy.interpolate
import numpy

# Call math function.
try: 
	#qvalue_list = qvalueold.estimate( numpy_pvalue_array )  # Old version.
	qvalue_obj = qvalue.QValue( pvalue_list )
	#qvalue_obj = qvalue.QValue( pvalue_list, scipy.arange(0.05,0.95,0.05), None, 3, 'smoother', False, True  )
	qvalue_list = qvalue_obj.qvalue()

except Exception as e:
	print ("The following error occured: {}<br>".format(e))


print ( "Output:<br>pvalue_list = " )
print ( pvalue_list )
print ( "<br>qvalue_list = " )
print ( qvalue_list )

#Temp start

sys.path.append( "{}/depend/libraries/".format(CGI_BIN_PATH) )  # Add the path to openpyxl, (excel files.)
from openpyxl import Workbook
import openpyxl

sys.path.append( "{}/depend/util_scripts/".format(CGI_BIN_PATH) )
import mailer

XLSX_FILENAME = "out_file"

wb = Workbook()
ws = wb.active
ws.title = "Data"

print("alive")

for item in qvalue_list:
	ws.append( [str(item)] )

print("stillalive")

file_text = openpyxl.writer.excel.save_virtual_workbook(wb)
file = mailer.create_file( XLSX_FILENAME, 'xlsx', file_text )

mailer.send_sfu_email("test_emailer", "gabriel_stang@sfu.ca", "Title", "body", [file])



#Temp end

	
##### Create a text file.


pass  # write to file.


##### Push file to the browser.

### Use this code to deploy file to browser.
#from shutil import copyfileobj
#import sys

#print("Content-type: application/octet-stream")
#print("Content-Disposition: attachment; filename=%s.zip" %(filename))
#print()

#with open('../../data/code/' + filename + '.zip','rb') as zipfile:
#    copyfileobj(zipfile, sys.stdout.buffer)

pass

print ( "<br><br> python version: " + sys.version )  # Print version number.
print ( "</body></html>" )  # Complete the html output.


