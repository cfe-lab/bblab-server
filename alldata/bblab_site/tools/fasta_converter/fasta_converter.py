# Checked for python 3.7
import cgi, sys, re, os
from django.http import HttpResponse


def run(fasta_data, button, delim, splitfastaheader, stripwhitespace):	
	
	output_string = ""
	is_download = False


	##### Function Definitions
	
	
	def checkFasta(string):
		if not '>' in string:
			return (1, '<span style="color:red;"><b>ERROR:</span> could not find the \'>\' character in data,</b> did you input fasta data?')
		elif not '\n' in string:
			return (1, '<span style="color:red;"><b>ERROR:</span> could not find any newline in data,</b> did you input fasta data?')
		else:
			return (0, string)

	# This accepts csv or tsv but they cannot mix characters.
	def checkCsv(string):
		if not '\t' in string and not ',' in string:
			return (1, '<span style="color:red;"><b>ERROR:</span> could not find any common delimiters in data,</b> did you input csv data?')
		elif '\t' in string and ',' in string:
			return (1, '<span style="color:red;"><b>ERROR:</span> data cannot contain a mix of tabs and comma characters,</b> is something wrong with your data?')
		else: 
			return (0, string)  # Default case

	def toFasta(lines, delim="_"):
		lines = [ [(delim).join(x.rstrip().replace(',', '\t').split('\t')[:-1]), x.rstrip().replace(',', '\t').split('\t')[-1]] for x in lines.split('\n')]
		return lines
	
	def toCsv(lines):
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
			out_str = """<!DOCTYPE html><html><head>
				<link rel="stylesheet" href="../tools/fasta_converter/css/style.css">
				</head><body><div class="container textoverflow">"""
		elif contenttype == CONTENT_HTML_TABLE:
			out_str = """<!DOCTYPE html><html><head>
				<link rel="stylesheet" href="../tools/fasta_converter/css/style.css">
				</head><body><div class="container textoverflow"><table>"""	
		return out_str
	
	def printContentClose(contenttype):
		if contenttype == CONTENT_HTML:
			out_str = """</div></body>\r\n</html>"""
		elif contenttype == CONTENT_HTML_TABLE:
			out_str = "</table></div></body></html>" 	
		return out_str
	
	
	##### Error checking code

	
	if button == "runfasta" or button == "dlfasta":
		validate = checkCsv(fasta_data)	
	else:
		validate = checkFasta(fasta_data)
		
	if validate[0] == 0:
		strprocess = validate[1]
	else:
		return (False, validate[1])
	

	##### Conversion Code
	

	try:
		if button == "runfasta":
			is_download = False
			
			output_string += printContentOpen(CONTENT_HTML)
			result = toFasta(strprocess,delim)
			for item in result:
				if (stripwhitespace):
					tbl = str.maketrans(dict.fromkeys(' '))
					output_string += ( ">{}<br>".format(item[0].translate(tbl)) )
				else:
					output_string += ( ">{}<br>".format(item[0]) )
				output_string += ( "{}<br>".format(item[1]) )
			output_string += printContentClose(CONTENT_HTML)
		
		elif button == "dlfasta":
			file_ex = "fa"
			is_download = True
			
			result = toFasta(strprocess,delim)
			for item in result:
				if (stripwhitespace):		
					tbl = str.maketrans(dict.fromkeys(' '))
					output_string += ( ">{}\r\n".format(item[0].translate(tbl)) )
				else:
					output_string += ( ">{}\r\n".format(item[0]) )
				output_string += ( "{}\r\n".format(item[1]) )
			
		elif button == "runcsv":
			is_download = False
			
			output_string += printContentOpen(CONTENT_HTML_TABLE)
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
							output_string += ( "<td>{}</td>".format(i) )
					else:
						output_string += ( "<tr><td>{}</td>".format(item[1:]) )
					header = False
				else:
					output_string += ( "<td>{}</td></tr>".format(item) )
					header = True
			output_string += printContentClose(CONTENT_HTML_TABLE)
		
		elif button == "dlcsv":
			file_ex = "csv"
			is_download = True
			
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
					output_string += ( "{},{}\r\n".format(header,item))
					isheader = True
	except Exception:
		return(False, "<b>Error running analysis,</b> is your data formatted properly?")

	# If the file is a download views.py uses filename in tuple[2]
	return (is_download, output_string, 'converted.{}'.format(file_ex) if is_download else "no filename")
