from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader, RequestContext, Template
from django.contrib.auth.decorators import login_required

def index(request):
    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"]=True
        context["username"]=request.user.username
    return render(request, "unique_sequence/index.html", context)

# This function activates the cgi script.
def results(request):
    if request.method == 'POST':
        # Process data a bit
        data = request.POST

        # Read file in chunks if it exists.
        if 'file' in data:
            fasta_data = data['fastaInputArea']
        else:
            fasta_data = b''  # This is a bytestring
            for chunk in request.FILES['file'].chunks():
                fasta_data += chunk
            fasta_data = fasta_data.decode("utf-8")

        email_address = data['emailAddress']

        # Run actual calulation (by passing data)
        from . import unique_sequence
        output_t = unique_sequence.run(fasta_data, email_address)
        template = Template(output_t)

        context = RequestContext(request)
        return HttpResponse(template.render(context))
    else:
        return HttpResponse("Please use the form to submit data.")
