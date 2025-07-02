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
					 stdout=tmpf, stderr=subprocess.PIPE) 
		proc.wait()
		
		# Check for R script errors
		if proc.returncode != 0:
			_, stderr = proc.communicate()
			raise RuntimeError(f"R script failed with return code {proc.returncode}: {stderr.decode('utf-8') if stderr else 'Unknown error'}")
		
		tmpf.seek(0)
		raw_output = tmpf.read().decode("utf-8").strip()
		
		# Handle empty output
		if not raw_output:
			raise RuntimeError("R script produced no output")
		
		# Robust parsing: handle both comma-separated and space-separated formats
		if ',' in raw_output:
			# Comma-separated format (new R versions)
			qvalue_strings = raw_output.split(',')
		else:
			# Space-separated format (old R versions)
			qvalue_strings = raw_output.split()
		
		# Convert to floats, filtering empty strings
		qvalues = []
		for qstr in qvalue_strings:
			qstr = qstr.strip()
			if qstr:
				try:
					qvalues.append(float(qstr))
				except ValueError:
					# Skip invalid values but log the issue
					continue
		
		# Validate that we got the expected number of q-values
		if len(qvalues) != len(pvalues):
			raise RuntimeError(f"R script returned {len(qvalues)} q-values but expected {len(pvalues)} (input p-values: {len(pvalues)})")
	
	return qvalues
