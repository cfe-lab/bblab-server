from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader, RequestContext, Template
from django.contrib.auth.decorators import login_required

def index(request):
    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"]=True
        context["username"]=request.user.username
    return render(request, "qvalue/index.html", context)

# This function activates the cgi script.
def results(request):
    if request.method == 'POST':
        # Process data a bit
        data = request.POST

        # Read file in chunks if it exists.
        pvalue_string = data['pValues']

        # Run actual calulation (by passing data)
        from . import qvalue_generate_file
        output_t = qvalue_generate_file.run(pvalue_string)
        if output_t[0] == False:	
                template = Template(output_t[1])
                context = RequestContext(request)
                return HttpResponse(template.render(context))
        else:
                return output_t[1]
    else:
        return HttpResponse("Please use the form to submit data.")
