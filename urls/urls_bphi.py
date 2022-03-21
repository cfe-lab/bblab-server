from django.urls import path, include
from django.shortcuts import redirect

# I put the function here cause it looks nice, hope thats fine. (-_^)
def tool_redirect(request):
	return redirect('/django/wiki/')

urlpatterns = [
	path('best_prob_HLA_imputation/', include('tools.best_prob_HLA_imputation.urls')),
	path('', tool_redirect),
]

