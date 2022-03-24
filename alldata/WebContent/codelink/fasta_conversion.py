#!/lib/anaconda3/bin/python3.7
import cgi, sys, re

form = cgi.FieldStorage()
forminput = form.getvalue("textinput")
runfasta = form.getvalue("runfasta")
dlfasta = form.getvalue("dlfasta")
runcsv = form.getvalue("runcsv")
dlcsv = form.getvalue("dlcsv")
delim = form.getvalue("delim")
splitfastaheader = form.getvalue("splitfastaheader")
stripwhitespace = form.getvalue("stripwhitespace")

if "datafile" in form:
	fileitem = form["datafile"]
else:
	fileitem = ""

##### Function Definitions


def toFasta(lines, delim="_"):
	lines = [[(delim).join(x.rstrip().split('\t')[:-1]), x.rstrip().split('\t')[-1]] for x in lines.split('\n')]
	return lines

def toCsv(lines):
	#result = re.findall('(>.+[\\n\\r\\n])([XVLIMFWPSCYNQDEKRH\\*\\-ACTGRYKMSWBHDVN\\:\\n\\r\\n]+)', lines, re.IGNORECASE)
	result = re.findall(r'(>.+[\n\r]+)([^>]+)',lines,re.IGNORECASE)	
	tbl = str.maketrans(dict.fromkeys('\n\r\n'))
	result = [y.translate(tbl).upper() for x in result for y in x]
	return result

CONTENT_HTML = 0
CONTENT_FILE_FASTA = 1
CONTENT_HTML_TABLE = 2
CONTENT_FILE_CSV = 3
def printContentOpen(contenttype):
	if contenttype == CONTENT_HTML:
		print( "Content-Type: text/html \r\n")
		print( """<!DOCTYPE html><html><head>
			<link rel="stylesheet" href="../tools/fasta_converter/css/style.css">
			</head><body><div class="container textoverflow">""" )
	elif contenttype == CONTENT_FILE_FASTA:
		print( "Content-Disposition: attachment; filename=\"converted.fa\"" )
		print( "Content-Type:application/octet-stream; name=\"converted.fa\"\r\n" ) 
	
	elif contenttype == CONTENT_HTML_TABLE:
		print( "Content-Type: text/html\r\n" )
		print( """<!DOCTYPE html><html><head>
			<link rel="stylesheet" href="../tools/fasta_converter/css/style.css">
			</head><body><div class="container textoverflow"><table>""" )	
	elif contenttype == CONTENT_FILE_CSV:
		print( "Content-Disposition: attachment; filename=\"converted.csv\"" )
		print( "Content-Type:application/octet-stream; name=\"converted.csv\"\r\n" ) 

def printContentClose(contenttype):
	if contenttype == CONTENT_HTML:
		print( """</div></body>\r\n</html>""" )
	elif contenttype == CONTENT_HTML_TABLE:
		print( "</table></div></body></html>" )		


##### Initial Data Processing


# Assign proper value to the string that will be processed.
if hasattr(fileitem, 'filename') and fileitem.filename:
	strprocess = str(fileitem.value.decode("utf-8"))
else:
	strprocess = forminput


##### Conversion Code


if (runfasta is not None):
	printContentOpen(CONTENT_HTML)
	result = toFasta(strprocess,delim)
	for item in result:
		if (stripwhitespace):
			tbl = str.maketrans(dict.fromkeys(' '))
			print( ">{}<br>".format(item[0].translate(tbl)) )
		else:
			print( ">{}<br>".format(item[0]) )
		print( "{}<br>".format(item[1]) )
	printContentClose(CONTENT_HTML)

elif (dlfasta is not None):
	printContentOpen(CONTENT_FILE_FASTA)
	result = toFasta(strprocess,delim)
	for item in result:
		if (stripwhitespace):		
			tbl = str.maketrans(dict.fromkeys(' '))
			print( ">{}".format(item[0].translate(tbl)) )
		else:
			print( ">{}".format(item[0]) )
		print( "{}".format(item[1]) )

elif (runcsv is not None):
	printContentOpen(CONTENT_HTML_TABLE)
	result = toCsv(strprocess)
	header = True
	for item in result:
		if (header is True):
			# js forces this to be false if delimiter is whitespace
			if (stripwhitespace):
				tbl = str.maketrans(dict.fromkeys(' '))
				item = item.translate(tbl)
			if (splitfastaheader):
				for i in item[1:].split(delim):
					print( "<td>{}</td>".format(i) )
			else:
				print( "<tr><td>{}</td>".format(item[1:]) )
			header = False
		else:
			print( "<td>{}</td></tr>".format(item) )
			header = True
	printContentClose(CONTENT_HTML_TABLE)

elif (dlcsv is not None):
	printContentOpen(CONTENT_FILE_CSV)
	result = toCsv(strprocess)
	isheader = True
	for item in result:
		if (isheader is True):
			if (stripwhitespace):		
				tbl = str.maketrans(dict.fromkeys(' '))
				item = item.translate(tbl)
			header = ''
			if (splitfastaheader):
				header = (',').join(item[1:].split(delim))
			else:
				header = item[1:]
			isheader = False
		else:
			print( "{},{}".format(header,item))
			isheader = True

