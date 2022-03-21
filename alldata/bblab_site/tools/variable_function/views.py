from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader, RequestContext, Template
from django.contrib.auth.decorators import login_required

def index(request):
    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"]=True
        context["username"]=request.user.username
    return render(request, "variable_function/index.html", context)

# This function activates the cgi script.
def results(request):
    if request.method == 'POST':
        # Process data a bit
        data = request.POST

        # Read file in chunks if it exists.
        textinput = data['textinput']

        if 'csv' in data:
            isCsv = True
        elif 'run' in data:
            isCsv = False

        # Run actual calulation (by passing data)
        from . import variable_function
        output_t = variable_function.run(textinput, isCsv)
        if output_t[0] == False:  # output_t[0] == is_download
            template = Template(output_t[1])
            context = RequestContext(request)
            return HttpResponse(template.render(context))
        else:
            response = HttpResponse(output_t[1], content_type="application/octet-stream")
            response['Content-Disposition'] = 'attachment; filename={}'.format(output_t[2])
            return response
    else:
        return HttpResponse("Please use the form to submit data.")
