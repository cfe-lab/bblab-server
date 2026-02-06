from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader, RequestContext, Template
from django.contrib.auth.decorators import login_required
from io import StringIO


def index(request):
    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"] = True
        context["username"] = request.user.username
    return render(request, "isoforms_plot/index.html", context)


def download_default(request):
    """Provide the default CSV file for download."""
    from . import run_isoforms

    csv_content = run_isoforms.get_default_csv()

    response = HttpResponse(csv_content, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="example_isoforms.csv"'
    return response


# This function activates the cgi script.
def use_example(request):
    """Generate plot using the default example CSV."""
    from . import run_isoforms

    # Get default CSV content
    csv_content = run_isoforms.get_default_csv()
    csv_data = StringIO(csv_content)

    # Generate plot
    result = run_isoforms.run(csv_data)

    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"] = True
        context["username"] = request.user.username

    if result["success"]:
        context["svg_path"] = result["svg_path"]
    else:
        context["error_message"] = result["error_message"]
        context["error_details"] = result.get("error_details")

    return render(
        request, "isoforms_plot/templates/isoforms_plot/results.html", context
    )


def results(request):
    if request.method == "POST":
        # Read file
        csv_data = StringIO(request.FILES["file"].read().decode("utf-8"))

        # Run actual calculation (by passing data)
        from . import run_isoforms

        result = run_isoforms.run(csv_data)

        context = {}
        if request.user.is_authenticated:
            context["user_authenticated"] = True
            context["username"] = request.user.username

        if result["success"]:
            context["svg_path"] = result["svg_path"]
        else:
            context["error_message"] = result["error_message"]
            context["error_details"] = result.get("error_details")

        return render(
            request, "isoforms_plot/templates/isoforms_plot/results.html", context
        )
    else:
        return HttpResponse("Please use the form to submit data.")
