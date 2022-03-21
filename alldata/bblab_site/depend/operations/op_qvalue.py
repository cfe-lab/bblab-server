# This module is compatible with python 3.7 #

import subprocess
import tempfile
import os

def get_qvalues( pvalues ):
	''' 
	This function uses the r script to convert a list of pvalues into
	a list of qvalues.

	Depends On: R
	'''

	# This block runs the R script from the using the commandline and converts the console output into a list.
	qvalues = []
	with tempfile.TemporaryFile() as tmpf:
		proc = subprocess.Popen(['Rscript', '{}qvalue_calculate.r'.format(os.environ.get('BBLAB_R_PATH', 'fail')), str(pvalues)],
					 stdout=tmpf) 
		proc.wait()
		tmpf.seek(0)
		qvalues = tmpf.read().decode("utf-8").replace(',', '').split(' ')[:-1]  # Converts the R script output into a list.
	qvalues = [float(qstr) for qstr in qvalues]
	
	return qvalues
