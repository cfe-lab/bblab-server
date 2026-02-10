from django.shortcuts import render
from django.http import HttpResponse
from io import StringIO


def _build_context(request, show_results=False, result=None):
    """Build template context with authentication and optional results."""
    context = {"show_results": show_results}

    if request.user.is_authenticated:
        context["user_authenticated"] = True
        context["username"] = request.user.username

    if result:
        if result["success"]:
            context["svg_path"] = result["svg_path"]
        else:
            context["error_message"] = result["error_message"]
            context["error_details"] = result.get("error_details")

    return context


def index(request):
    return render(request, "isoforms_plot/index.html", _build_context(request))


def download_default(request):
    """Provide the default CSV file for download."""
    from . import run_isoforms

    csv_content = run_isoforms.get_default_csv()

    response = HttpResponse(csv_content, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="example_isoforms.csv"'
    return response


def use_example(request):
    """Generate plot using the default example CSV."""
    from . import run_isoforms

    csv_content = run_isoforms.get_default_csv()
    csv_data = StringIO(csv_content)
    result = run_isoforms.run(csv_data)

    context = _build_context(request, show_results=True, result=result)
    return render(request, "isoforms_plot/index.html", context)


def results(request):
    if request.method == "POST":
        from . import run_isoforms

        try:
            csv_file = request.FILES["file"]
        except KeyError:
            context = _build_context(request, show_results=False)
            return render(request, "isoforms_plot/index.html", context)

        result = run_isoforms.run(csv_file)

        context = _build_context(request, show_results=True, result=result)
        return render(request, "isoforms_plot/index.html", context)
    else:
        return HttpResponse("Please use the form to submit data.")
