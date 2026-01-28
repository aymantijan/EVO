from django.core.management.base import BaseCommand
from django.db.models import Q
from gamification.models import Resource
import csv
from pathlib import Path


class Command(BaseCommand):
    help = 'Import resources (Books, Articles, Movies, Podcasts, Mentors) from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip if resource title already exists'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing resources by title'
        )
        parser.add_argument(
            '--type',
            type=str,
            help='Filter by type (Livre, Article, FilmSérie, Podcast, Mentor)'
        )

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        skip_duplicates = options.get('skip_duplicates', False)
        update_existing = options.get('update', False)
        filter_type = options.get('type', None)

        if not Path(csv_path).exists():
            self.stdout.write(self.style.ERROR(f'❌ Fichier non trouvé: {csv_path}'))
            return

        imported = 0
        updated = 0
        skipped = 0
        errors = 0

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')

                if not reader.fieldnames:
                    self.stdout.write(self.style.ERROR('❌ CSV vide ou format invalide'))
                    return

                # Vérifier les colonnes requises
                required_fields = {'titre', 'auteur', 'type', 'domaine', 'description', 'niveau'}
                if not required_fields.issubset(set(reader.fieldnames or [])):
                    self.stdout.write(
                        self.style.ERROR(
                            f'❌ Colonnes manquantes. Requises: {required_fields}'
                        )
                    )
                    return

                self.stdout.write(self.style.SUCCESS('📖 Début de l\'importation...'))

                for idx, row in enumerate(reader, 1):
                    try:
                        # Nettoyer les données
                        titre = row.get('titre', '').strip()
                        auteur = row.get('auteur', '').strip()
                        type_ressource = row.get('type', '').strip()
                        domaine = row.get('domaine', '').strip()
                        description = row.get('description', '').strip()

                        # Vérifier les données obligatoires
                        if not all([titre, auteur, type_ressource, domaine, description]):
                            self.stdout.write(
                                self.style.WARNING(
                                    f'⏭️  Ligne {idx}: Données obligatoires manquantes'
                                )
                            )
                            skipped += 1
                            continue

                        # Valider le type
                        valid_types = ['Livre', 'Article', 'FilmSérie', 'Podcast', 'Mentor']
                        if type_ressource not in valid_types:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'⏭️  Ligne {idx}: Type "{type_ressource}" invalide. '
                                    f'Utilisez: {", ".join(valid_types)}'
                                )
                            )
                            skipped += 1
                            continue

                        # Filtrer par type si demandé
                        if filter_type and type_ressource != filter_type:
                            skipped += 1
                            continue

                        # Valider le niveau
                        try:
                            niveau = int(row.get('niveau', '1'))
                            if not (1 <= niveau <= 1000):
                                raise ValueError('Niveau doit être entre 1 et 1000')
                        except (ValueError, TypeError):
                            self.stdout.write(
                                self.style.WARNING(
                                    f'⏭️  Ligne {idx}: Niveau invalide "{row.get("niveau")}". '
                                    f'Utilisation du défaut: 1'
                                )
                            )
                            niveau = 1

                        # Vérifier si la ressource existe
                        existing = Resource.objects.filter(titre=titre).first()

                        if existing:
                            if update_existing:
                                # Mettre à jour
                                existing.auteur = auteur
                                existing.type = type_ressource
                                existing.domaine = domaine
                                existing.description = description
                                existing.niveau = niveau
                                existing.url = row.get('url', '')
                                existing.image = row.get('image', '')

                                is_active = row.get('is_active', 'true').lower()
                                existing.is_active = is_active in ('true', '1', 'yes', 'oui')

                                existing.save()
                                updated += 1
                                self.stdout.write(f'  🔄 {titre}')
                            elif skip_duplicates:
                                skipped += 1
                            else:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'⏭️  Ligne {idx}: "{titre}" existe déjà. '
                                        f'Utilisez --update ou --skip-duplicates'
                                    )
                                )
                                skipped += 1
                        else:
                            # Créer nouvelle ressource
                            is_active = row.get('is_active', 'true').lower()
                            is_active = is_active in ('true', '1', 'yes', 'oui')

                            Resource.objects.create(
                                titre=titre,
                                auteur=auteur,
                                type=type_ressource,
                                domaine=domaine,
                                description=description,
                                niveau=niveau,
                                url=row.get('url', ''),
                                image=row.get('image', ''),
                                is_active=is_active
                            )
                            imported += 1

                            # Afficher type emoji
                            type_emoji = {
                                'Livre': '📚',
                                'Article': '📰',
                                'FilmSérie': '🎬',
                                'Podcast': '🎙️',
                                'Mentor': '👨‍🏫'
                            }
                            emoji = type_emoji.get(type_ressource, '📄')
                            self.stdout.write(f'  ✅ {emoji} {titre}')

                    except Exception as e:
                        errors += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'❌ Ligne {idx}: {str(e)}'
                            )
                        )
                        continue

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur fichier: {str(e)}'))
            return

        # Résumé
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('📊 RÉSUMÉ DE L\'IMPORTATION'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'✅ Importés: {imported}')
        self.stdout.write(f'🔄 Mis à jour: {updated}')
        self.stdout.write(f'⏭️  Ignorés: {skipped}')
        self.stdout.write(self.style.ERROR(f'❌ Erreurs: {errors}'))
        self.stdout.write(self.style.SUCCESS(f'📚 Total: {imported + updated} ressources ajoutées/mises à jour'))
        self.stdout.write(self.style.SUCCESS('=' * 60))