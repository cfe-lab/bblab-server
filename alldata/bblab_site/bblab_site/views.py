import os
from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings

# This function redirects from the root directory to the wiki.  
# '/' -> '/wiki/'
def root_redirect(request):
	return redirect("/django/wiki/")

def version(request):
	"""Return the git version of the container."""
	version_file = '/BBLAB_SITE_VERSION'

	with open(version_file, 'r') as f:
		git_version = f.read().strip()

	return JsonResponse({
		'version': git_version,
		'build_date': os.environ.get('BUILD_DATE', 'n/a'),
		'build_user': os.environ.get('BUILD_USER', 'n/a'),
	})
