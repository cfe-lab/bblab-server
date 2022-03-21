# Checked for python 3.7
import cgi, sys

def run(userinput, button):
	
	out_str = ""

	def printHtmlHeaders():
		return ("""{% load static %}<!DOCTYPE html><html><head>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
		<script src="{% static "bphi_script.js" %}"></script>
		<link rel="stylesheet" href="{% static "/bphi_css/style.css" %}"></head><body>""")
	
	def makeD(lines):
		tbl = str.maketrans(dict.fromkeys('\r'))
		lines = lines.translate(tbl).strip()
		lines = lines.split('\n')[2:]
		lines = [x.split('\t') for x in lines]
		
		d = {}
		for line in lines[1:]:
			if (line[0] not in d):
				d[line[0]] = [line[1:]]
			else:
				d[line[0]].append(line[1:])	
		return d
	
	if button == "run":
		is_download = False
		out_str += printHtmlHeaders()+'<div class="container">'
		d = makeD(userinput)
		
		out_str += """<table> <tr>
			<th>pid</th>
			<th>A1</th>
			<th>A2</th>
			<th>B1</th>
			<th>B2</th>
			<th>C1</th>
			<th>C2</th>
			<th>Probability</th>
			<th>Ethnicity</th>
			<th>Error</th> </tr>"""

		for id in list(d.keys()):
			item = '<td>'+id+'</td><td>'+('</td><td>').join(sorted([x for x in d[id]],key=lambda x: x[-1], reverse=True)[0])+'</td>'
			out_str += '<tr>{}</tr>'.format(item)
		
		out_str += '</table>'

	elif button == "dl":
		is_download = True
		out_str += "pid,A1,A2,B1,B2,C1,C2,Probability,Ethnicity,Error\r\n"
		d = makeD(userinput)
		for id in list(d.keys()):
			out_str += id+','+','.join(sorted([x for x in d[id]],key=lambda x: x[-1], reverse=True)[0])+'\r\n'

	return (is_download, out_str, "best_prob_HLA_imputation.csv")
