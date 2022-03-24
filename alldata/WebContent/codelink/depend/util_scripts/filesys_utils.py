# This is Python 3.6
import os
import datetime

def archive_in_dir(current_dir_path, archive_path, age):
	'''
	This function moves files in one directory that are more than $age days old
	into the archive directory.
	$age -> [int] days.
	'''
	print ( "<br><br>Archiving files older than {} days.<br>".format( age ) )

	# for finding all files in a directory.
	files_archived = 0
	for filename in os.listdir( current_dir_path ):
		if filename[0] != '.':  # Only loop visible files.
			file_path = current_dir_path + filename  # Path to the file.
			
			# Find how many days ago the file was created.
			modified = os.path.getmtime(file_path)  # Get time last modified.
			modified = datetime.datetime.fromtimestamp(modified)  # Convert time to datetime.
			now = datetime.datetime.now()
			days = (now-modified).days
			
			# Move files that are too old to a new directory.
			if days >= age:
				files_archived += 1
				os.rename(file_path, archive_path + filename)
				print ( "Archiving " + str(filename) + ' at ' + str(days) + ' days old.<br>' ) 

	print ( "Total files archived : {}<br>".format(files_archived) )

