from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader, RequestContext, Template

def index(request):
    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"]=True
        context["username"]=request.user.username
    return render(request, "best_prob_HLA_imputation/index.html", context)

# This function activates the cgi script.
def results(request):
    if request.method == 'POST':
        # Process data a bit
        data = request.POST
 
        # Read file in chunks if it exists.
        userinput = data['userinput']

        if "runbestprob" in data:
                button = "run"
        elif "dlbestprob" in data:
                button = "dl"

        # Run actual calulation (by passing data)
        from . import best_prob_HLA_imputation
        output_t = best_prob_HLA_imputation.run(userinput, button)
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
