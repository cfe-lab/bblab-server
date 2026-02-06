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
    return render(request, "isoforms_plot/index.html", context)


def download_default(request):
    """Provide the default CSV file for download."""
    from . import run_isoforms
    csv_content = run_isoforms.get_default_csv()
    
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="example_isoforms.csv"'
    return response


# This function activates the cgi script.
def results(request):
    if request.method == 'POST':
        # Process data a bit
        data = request.POST

        # Read file
        csv_data = StringIO(request.FILES['file'].read().decode("utf-8"))

        email_address = data.get('emailAddress', '')
        desc = data.get('analysisID', '')

        # Run actual calulation (by passing data)
        from . import run_isoforms
        output_t = run_isoforms.run(csv_data, desc, email_address)
        template = Template(output_t)

        context = RequestContext(request)
        return HttpResponse(template.render(context))
    else:
        return HttpResponse("Please use the form to submit data.")
