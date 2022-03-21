from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader, RequestContext, Template

def index(request):
    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"]=True
        context["username"]=request.user.username
    return render(request, "phage_i_expanded/index.html", context)

# This function activates the cgi script.
def results(request):
    if request.method == 'POST':
        # Process data a bit
        data = request.POST

        # Get main inputs.
        hlas = data['hlas_input']
        patients = data['patients_input']

        protein = data['protein_selection']

        if "runPHAGE" in data:
            button = "run"
        elif "dlPHAGE" in data:
            button = "dl"

        # Run actual calulation (by passing data)
        from .scripts import PHAGE
        output_t = PHAGE.run(hlas, patients, protein, button)
        if output_t[0] == False:  # output_t[0] is is_download
            template = Template(output_t[1])
            context = RequestContext(request)
            return HttpResponse(template.render(context))
        else:
            response = HttpResponse(output_t[1], content_type="application/octet-stream")
            response['Content-Disposition'] = 'attachment; filename={}'.format(output_t[2])
            return response
    else:
        return HttpResponse("Please use the form to submit data.")