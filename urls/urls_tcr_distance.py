from django.urls import path, include
from django.shortcuts import redirect

# I put the function here cause it looks nice, hope thats fine. (-_^)
def tool_redirect(request):
	return redirect('/django/wiki/')

urlpatterns = [
	path('tcr_distance/', include('tools.tcr_distance.urls')),
	path('', tool_redirect),
]

