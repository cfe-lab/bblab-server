"""
WSGI config for bblab_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os, sys

print("Python path = ", sys.path, file=sys.stderr)
print("Current dir", os.getcwd(), file=sys.stderr)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bblab_site.settings')

application = get_wsgi_application()
