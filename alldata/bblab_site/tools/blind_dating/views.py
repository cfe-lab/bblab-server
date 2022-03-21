from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader, RequestContext, Template
from django.contrib.auth.decorators import login_required
import logging
from . import blind_dating
import os
import pathlib
import tempfile
from .models import DatingOutput

SELF_PATH = pathlib.Path(__file__).parent.absolute()
OUTPUT_PATH = os.path.join(SELF_PATH, 'output')

def index(request):
    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"]=True
        context["username"]=request.user.username
    return render(request, "blind_dating/index.html", context)


# This function activates the cgi script.
def results(request):
    if request.method == 'POST':
        # Process data a bit
        data = request.POST

        email_address = data['emailAddress']

        tree_file = save_data_from_input(request, 'tree_file')

        test_write(os.path.join(OUTPUT_PATH, 'test.txt'), b'hello!')

        # Run actual calulation (by passing data)
        output_t = blind_dating.get_html_results(tree_file)
        template = Template(output_t)
        context = RequestContext(request)
        return HttpResponse(template.render(context))
    else:
        return HttpResponse("Please use the form to submit data.")

def test_write(path, data):
    with open(path, 'wb+') as o:
        o.write(data)

def save_data_from_input(request, input_name):
    tf = tempfile.TemporaryFile()
    for chunk in request.FILES[input_name].chunks():
        tf.write(chunk)
    tf.seek(0)
    return tf

def download(content):
    return
