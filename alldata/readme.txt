This file is describing what the purpose of the three directories here are.

"WebContent/" -> This directory holds the 'raw' apache webserver files. This is the original migration of tools that did not use django (the 'old webserver'). The scripts for this implementation are stored elsewhere. Before deleteing the old webserver, make sure to update the saved user data from the plate layout tools to the django tools.

"bblab_site/" -> This directory is the new django section of the webserver. It contains a working wiki written in python.

"hla_class/"  -> This directory contains the hla class tool. The djano part of the webserver isn't hosting this tool because it isn't written in python. There is a special case written in the apache server config file to host this file just using apache.

