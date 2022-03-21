from django.shortcuts import render
from django.http import HttpResponse
from django.template import Template, RequestContext

import os, sys

from django.contrib.auth.decorators import login_required

# UTIL_PATH = "/alldata/bblab_site/depend/util_scripts"
# sys.path.append(UTIL_PATH)
from depend.util_scripts import django_utils

def index(request):
	context={}
	if request.user.is_authenticated:
		context["user_authenticated"]=True
		context["username"]=request.user.username
	return render(request, 'sequencing_layout/index.html', context)


def generate_files(request):
	if request.method == "POST":
		data = request.POST
		
		input_str = data['manualFields']
		username = data['userName']
		plate_id = data['plateID']
		email_address = data['emailAddress']
		machine = data['sequencingMachine']		

		# Run actual calculatiuon
		from . import sequencing_generate_files
		output_t = sequencing_generate_files.run(input_str, username, plate_id, email_address, machine)
		template = Template(output_t)

		context = RequestContext(request)	
		return HttpResponse(template.render(context))
	else:
		return HttpResponse("Please use the form to submit data.")


##### Directory Display Functions #####

@login_required
def output(request, filename=None):
	if filename == None:
		template = Template(django_utils.dir_index_str( "output/", request, "/django/tools/sequencing_layout/", __file__ ))
		context = RequestContext(request)
		context["user_authenticated"]=True
		context["username"]=request.user.username
		return HttpResponse(template.render(context))
	else:	
		return django_utils.read_file(filename, "output/", __file__)

@login_required
def archive(request, filename=None):
	if filename == None:
		template = Template(django_utils.dir_index_str( "output/archived_layouts/", request, 
							        "/django/tools/sequencing_layout/output/", __file__ ))
		context = RequestContext(request)
		context["user_authenticated"]=True
		context["username"]=request.user.username
		return HttpResponse(template.render(context))
	else:	
		return django_utils.read_file(filename, "output/archived_layouts/", __file__)

@login_required
def old_archive(request, filename=None):
	if filename == None:
		template = Template(django_utils.dir_index_str( "output/archived_layouts/old_archived_layouts/", 
							        request, "/django/tools/sequencing_layout/output/archived_layouts/", __file__ ))
		context = RequestContext(request)
		context["user_authenticated"]=True
		context["username"]=request.user.username
		return HttpResponse(template.render(context))
	else:
		return django_utils.read_file(filename, "output/archived_layouts/old_archived_layouts/", __file__)
