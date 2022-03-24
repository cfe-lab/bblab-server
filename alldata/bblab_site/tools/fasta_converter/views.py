from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader, RequestContext, Template
from django.contrib.auth.decorators import login_required

def index(request):
    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"]=True
        context["username"]=request.user.username
    return render(request, "fasta_converter/index.html", context)

# This function activates the cgi script.
def calculate(request):
    if request.method == 'POST':
        # Process data a bit
        data = request.POST

        # Read file in chunks if it exists.
        if 'datafile' in data:
            fasta_data = data['textinput']
        else:
            fasta_data = b''  # This is a bytestring
            for chunk in request.FILES['datafile'].chunks():
                fasta_data += chunk
            fasta_data = fasta_data.decode("utf-8")

        # Determine which button is pressed (which analysis to run)	
        if "runfasta" in data:
                button = "runfasta"
        elif "dlfasta" in data:
                button = "dlfasta"
        elif "runcsv" in data:
                button = "runcsv"
        elif "dlcsv" in data:
                button = "dlcsv"
        else:
                button = "err"	
        
        delim = data['delim']
        splitfastaheader = data['splitfastaheader']
        stripwhitespace = data['stripwhitespace']

        # Run actual calulation (by passing data)
        from . import fasta_converter
        output_t = fasta_converter.run(fasta_data, button, delim, splitfastaheader, stripwhitespace)
        if output_t[0] == False:
                template = Template(output_t[1])
                context = RequestContext(request)
                return HttpResponse(template.render(context))
        else:
                response = HttpResponse(output_t[1], content_type="application/octet-stream")
                response['Content-Disposition'] = 'attachment; filename={}'.format(output_t[2])
                return response
    else:
        return HttpResponse("Please use the form to submit data.")
