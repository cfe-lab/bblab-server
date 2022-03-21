# This is Python 3.6
import os
import datetime

# TODO: make sure filenames cannot mess things up.
def archive_in_dir(current_dir_path, archive_path, age):
	'''
	This function moves files in one directory that are more than $age days old
	into the archive directory.
	$age -> [int] days.
	'''
	out_string = "<br>Archiving files older than {} days.<br>".format( age )

	# for finding all files in a directory.
	files_archived = 0
	for filename in os.listdir( current_dir_path ):
		if filename[0] != '.' and os.path.isfile(current_dir_path + filename):  # Only loop visible files. Don't do directories.
			file_path = current_dir_path + filename  # Path to the file.
			
			# Find how many days ago the file was created.
			modified = os.path.getmtime(file_path)  # Get time last modified.
			modified = datetime.datetime.fromtimestamp(modified)  # Convert time to datetime.
			now = datetime.datetime.now()
			days = (now - modified).days
			
			# Move files that are too old to a new directory.
			if days >= age:
				files_archived += 1
				
				file_index=0
				while os.path.isfile( archive_path+("v{}_".format(file_index) if file_index!=0 else "")+filename ):
					file_index += 1
				
				os.rename( file_path, archive_path+("v{}_".format(file_index) if file_index!=0 else "")+filename )
				out_string += ( "Archiving " + str(filename) + ' at ' + str(days) + ' days old.<br>' )
				out_string += ( "" if file_index==0 else "v{}_ has been prepended to {} because another file with the same name existed.<br>".format(file_index, filename) )
		
	out_string += "Total files archived : {}<br>".format(files_archived)
	return out_string

