from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader, RequestContext, Template
from django.contrib.auth.decorators import login_required
from io import StringIO


def index(request):
    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"]=True
        context["username"]=request.user.username
    return render(request, "proviral_landscape_plot/index.html", context)


# This function activates the cgi script.
def results(request):
    if request.method == 'POST':
        # Process data a bit
        data = request.POST

        # Read file
        csv_data = StringIO(request.FILES['file'].read().decode("utf-8"))

        email_address = data['emailAddress']
        desc = data['analysisID']

        # Run actual calulation (by passing data)
        from . import run_proviral_landscape
        output_t = run_proviral_landscape.run(csv_data, desc, email_address)
        template = Template(output_t)

        context = RequestContext(request)
        return HttpResponse(template.render(context))
    else:
        return HttpResponse("Please use the form to submit data.")
