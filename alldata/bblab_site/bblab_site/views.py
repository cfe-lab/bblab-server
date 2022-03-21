from django.shortcuts import redirect

# This function redirects from the root directory to the wiki.  
# '/' -> '/wiki/'
def root_redirect(request):
	return redirect("/django/wiki/")
