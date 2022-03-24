from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    context = {}
    if request.user.is_authenticated:
        context["user_authenticated"]=True
        context["username"]=request.user.username
    return render(request, "HIV_genome/index.html", context)

