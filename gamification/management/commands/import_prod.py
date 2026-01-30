import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamification_config.settings')
django.setup()

from gamification.models import Resource
import json

with open('resources.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

Resource.objects.all().delete()

for item in data:
    Resource.objects.create(
        titre=item.get('titre'),
        auteur=item.get('auteur'),
        type=item.get('type', 'Autre'),
        domaine=item.get('domaine', 'Autre'),
        description=item.get('description', ''),
        niveau=item.get('niveau', 1),
        url=item.get('url'),
        is_active=item.get('is_active', True),
    )

print(f"✅ {Resource.objects.count()} ressources importées!")
