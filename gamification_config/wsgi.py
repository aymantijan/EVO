"""
WSGI config for gamification_config project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamification_config.settings')
application = get_wsgi_application()
