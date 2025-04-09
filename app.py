import os

# Nahraďte "perfectbody" názvem hlavního modulu vašeho Django projektu
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "perfectbody.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()