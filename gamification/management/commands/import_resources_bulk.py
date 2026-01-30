from django.core.management.base import BaseCommand
from gamification.models import Resource
import json

class Command(BaseCommand):
    help = 'Import resources from JSON'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='resources.json')

    def handle(self, *args, **options):
        file_path = options['file']
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Vide les anciennes ressources
        Resource.objects.all().delete()
        
        # Crée les nouvelles
        created = 0
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
            created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {created} ressources importées!')
        )
