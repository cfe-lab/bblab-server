from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader, RequestContext, Template

def index(request):
    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"]=True
        context["username"]=request.user.username
    return render(request, "text_to_columns/index.html", context)

# This function activates the cgi script.
def results(request):
    if request.method == 'POST':
        # Process data a bit
        data = request.POST
 
        # Read file in chunks if it exists.
        userinput = data['userinput']

        if "runtranslate" in data:
                button = "run"
        elif "dltranslate" in data:
                button = "dl"

        # Run actual calulation (by passing data)
        from . import text_to_columns
        output_t = text_to_columns.run(userinput, button)
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
