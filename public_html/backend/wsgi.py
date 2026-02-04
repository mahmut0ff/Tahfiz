import os
import sys
import platform
sys.path.insert(0, '/home/c/cl17008/django_ksta7/public_html')
sys.path.insert(0, '/home/c/cl17008/django_ksta7/public_html/backend')
sys.path.insert(0, '/home/c/cl17008/django_ksta7/venv/lib/python3.10/site-packages')
os.environ["DJANGO_SETTINGS_MODULE"] = "backend.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
