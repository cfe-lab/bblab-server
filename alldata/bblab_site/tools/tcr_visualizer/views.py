from django.shortcuts import render


def index(request):
    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"]=True
        context["username"]=request.user.username
    return render(request, "tcr_visualizer/index.html", context)

