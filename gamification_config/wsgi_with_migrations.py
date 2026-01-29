import os
import sys
import django
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamification_config.settings')

# Exécute les migrations AVANT de charger l'app
try:
    django.setup()
    call_command('migrate', '--noinput', verbosity=0)
except Exception as e:
    print(f"Migration error: {e}", file=sys.stderr)

application = get_wsgi_application()
