from django.urls import path, include
from django.shortcuts import redirect

# I put the function here cause it looks nice, hope thats fine. (-_^)
def tool_redirect(request):
	return redirect('/django/wiki/')

urlpatterns = [
	path('unique_sequence/', include('tools.unique_sequence.urls')),
	path('', tool_redirect),
]

