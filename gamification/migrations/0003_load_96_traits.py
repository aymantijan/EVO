from django.db import migrations
from django.utils import timezone


def load_traits(apps, schema_editor):
    """Charge les 96 traits directement en BD"""
    PersonalityTrait = apps.get_model('gamification', 'PersonalityTrait')

    traits_data = [
        # COGNITIFS (15)
        ("Pensée Analytique", "Capacité à décomposer les problèmes complexes en éléments compréhensibles."),
        ("Pensée Logique", "Capacité à raisonner de façon cohérente et rigoureuse."),
        ("Pensée Critique", "Questionnement actif et évaluation d'hypothèses."),
        ("Pensée Stratégique", "Planification long terme et alignement d'objectifs."),
        ("Pensée Systémique", "Comprendre les interconnexions et interactions complexes."),
        ("Pensée Abstraite", "Capacité à conceptualiser et théoriser."),
        ("Pensée Intuitive", "Compréhension instinctive sans analyse consciente."),
        ("Créativité Intellectuelle", "Génération d'idées originales et innovantes."),
        ("Curiosité Intellectuelle", "Désir constant d'apprendre et d'explorer."),
        ("Vision Long Terme", "Capacité à anticiper et planifier l'avenir."),
        ("Flexibilité Mentale", "Capacité à adapter pensée et stratégie."),
        ("Rigidité Cognitive", "(TRAIT NÉGATIF) Résistance au changement."),
        ("Capacité d'Apprentissage", "Vitesse et efficacité à acquérir compétences nouvelles."),
        ("Lucidité", "Conscience claire de soi et du réel."),
        ("Esprit de Synthèse", "Capacité à résumer et combiner informations."),

        # ÉMOTIONNELS (13)
        ("Stabilité Émotionnelle", "Équilibre émotionnel et gestion des fluctuations."),
        ("Instabilité Émotionnelle", "(TRAIT NÉGATIF) Fluctuations émotionnelles excessives."),
        ("Résilience", "Capacité à rebondir après adversité."),
        ("Sang-Froid", "Maîtrise complète sous pression intense."),
        ("Sensibilité Émotionnelle", "Capacité à percevoir et résonner avec émotions."),
        ("Impulsivité Émotionnelle", "(TRAIT NÉGATIF) Réactions impulsives."),
        ("Maîtrise de Soi", "Autocontrôle et discipline émotionnelle."),
        ("Tolérance au Stress", "Capacité à fonctionner sous pression."),
        ("Vulnérabilité Émotionnelle", "Ouverture authentique et admission de fragilité."),
        ("Stoïcisme", "Acceptation philosophique de l'inévitable."),
        ("Détachement Émotionnel", "Distance objectif face situations personnelles."),
        ("Anxiété", "(TRAIT NÉGATIF) Inquiétude excessive."),
        ("Irritabilité", "(TRAIT NÉGATIF) Susceptibilité à la colère."),

        # COMPORTEMENTAUX (12)
        ("Discipline", "Autodiscipline et respect de standards."),
        ("Autocontrôle", "Contrôle du comportement et des impulses."),
        ("Persévérance", "Persistence malgré obstacles prolongés."),
        ("Rigueur", "Attention au détail et standards élevés."),
        ("Organisation", "Structuration et planification efficace."),
        ("Fiabilité", "Consistency et tenue des engagements."),
        ("Sens du Devoir", "Obligation morale et responsabilité."),
        ("Responsabilité", "Imputabilité et accountability."),
        ("Prudence", "Gestion des risques et prévention."),
        ("Gestion du Temps", "Utilisation efficace du temps disponible."),
        ("Capacité d'Exécution", "Talent à concrétiser les idées."),
        ("Constance dans l'Effort", "Effort soutenu et consistant."),

        # SOCIAUX (15)
        ("Sociabilité", "Aisance et plaisir en interactions sociales."),
        ("Assertivité", "Expression claire et confidente des besoins."),
        ("Charisme", "Attrait naturel et influence personnelle."),
        ("Influence", "Capacité à affecter opinions et actions."),
        ("Persuasion", "Art de convaincre par arguments."),
        ("Diplomatie", "Gestion tactful de relations difficiles."),
        ("Coopération", "Travail effectif en équipe."),
        ("Compétitivité", "Désir de gagner et d'exceller."),
        ("Individualisme", "Autonomie et indépendance d'esprit."),
        ("Conformisme", "Adaptation aux normes sociales."),
        ("Dominance Sociale", "Tendance à leadership et contrôle."),
        ("Subordination", "Acceptation d'autorité."),
        ("Agressivité Sociale", "(TRAIT NÉGATIF) Tendance au conflit."),
        ("Manipulation", "(TRAIT NÉGATIF) Contrôle malhonnête d'autres."),
        ("Empathie Relationnelle", "Compréhension des besoins autres."),

        # MORAUX (14)
        ("Intégrité", "Cohérence entre valeurs et actions."),
        ("Loyauté", "Fidélité aux personnes et principes."),
        ("Honneur", "Respect de dignité personnelle et autres."),
        ("Justice", "Équité et fairness."),
        ("Courage", "Brave face à peur et danger."),
        ("Tempérance", "Modération et équilibre."),
        ("Dignité", "Respect personnel et projection."),
        ("Responsabilité Morale", "Conscience éthique et accountability."),
        ("Bienveillance", "Bonté envers autres."),
        ("Altruisme", "Sacrifice pour bien d'autres."),
        ("Hypocrisie", "(TRAIT NÉGATIF) Paroles vs actions discordent."),
        ("Lâcheté", "(TRAIT NÉGATIF) Manque de courage."),
        ("Ressentiment", "(TRAIT NÉGATIF) Rancoeur entretenue."),
        ("Servilité", "(TRAIT NÉGATIF) Dignité compromise."),

        # SOMBRES (11)
        ("Narcissisme", "(TRAIT NÉGATIF) Besoin excessif d'admiration."),
        ("Machiavélisme", "(TRAIT NÉGATIF) Manipulation et manque scrupules."),
        ("Psychopathie", "(TRAIT NÉGATIF) Absence d'empathie et culpabilité."),
        ("Cynisme", "(TRAIT NÉGATIF) Doute systématique des motifs."),
        ("Égocentrisme", "(TRAIT NÉGATIF) Perspective autre ignorée."),
        ("Absence de Remords", "(TRAIT NÉGATIF) Mal fait sans remords."),
        ("Opportunisme Extrême", "(TRAIT NÉGATIF) Exploitation déloyale."),
        ("Cruauté", "(TRAIT NÉGATIF) Infliction intentionnelle de souffrance."),
        ("Paranoïa", "(TRAIT NÉGATIF) Méfiance exessive."),
        ("Sadisme", "(TRAIT NÉGATIF) Plaisir dans souffrance."),
        ("Manipulation Froide", "(TRAIT NÉGATIF) Jeu émotionnel calculé."),

        # MOTIVATIONNELS (10)
        ("Ambition", "Désir de succès et élévation."),
        ("Volonté", "Détermination et force de caractère."),
        ("Détermination", "Fermeté de but."),
        ("Goût du Pouvoir", "Désir d'influence et contrôle."),
        ("Tolérance au Risque", "Confort avec incertitude."),
        ("Recherche de Performance", "Orientation excellence."),
        ("Orientation Résultats", "Focus sur livrable et impact."),
        ("Besoin d'Accomplissement", "Satisfaction du faire/complétude."),
        ("Motivation Intrinsèque", "Motivation interne plutôt externe."),
        ("Motivation Extrinsèque", "Motivation par rewards externes."),

        # EXISTENTIELS (10)
        ("Autonomie", "Indépendance et autodétermination."),
        ("Affirmation de Soi", "Expression authentique de soi."),
        ("Volonté de Puissance", "Désir de surpasser limitations."),
        ("Sens du Destin", "Sensation de purpose prédéterminé."),
        ("Quête de Sens", "Recherche de meaning."),
        ("Nihilisme", "(TRAIT NÉGATIF) Sens nié systématiquement."),
        ("Acceptation de l'Absurde", "Paix avec incertitude existentielle."),
        ("Responsabilité Existentielle", "Accountability pour sa vie."),
        ("Individualité Forte", "Distinctiveness authentique."),
        ("Conscience de Soi", "Self-awareness profonde."),

        # LEADERSHIP (8)
        ("Leadership Naturel", "Capacité innée à diriger."),
        ("Autorité", "Légitimité de direction."),
        ("Gestion de Pression", "Performance sous stress extrême."),
        ("Sens Politique", "Navigation organisationnelle habile."),
        ("Capacité à Commander", "Direction de personnes effective."),
        ("Capacité à Déléguer", "Trust et empowerment."),
        ("Responsabilité Hiérarchique", "Accountability pour team."),
        ("Focalisation Objectifs", "Maintenance du focus collectif."),

        # AFFECTIFS (9)
        ("Empathie Émotionnelle", "Résonance authentique aux émotions."),
        ("Compassion", "Souci et désiré d'aider."),
        ("Attachement", "Lien émotionnel profond."),
        ("Détachement Affectif", "Distance émotionnelle objective."),
        ("Dépendance Affective", "(TRAIT NÉGATIF) Besoin excessif d'autres."),
        ("Fierté", "Dignité et satisfaction personnelle."),
        ("Honte", "(TRAIT NÉGATIF) Culpabilité destructive."),
        ("Culpabilité", "Responsabilité morale ressentie."),
        ("Besoin de Reconnaissance", "Validation externe désirée."),
    ]

    now = timezone.now()
    for name, description in traits_data:
        PersonalityTrait.objects.get_or_create(
            name=name,
            defaults={
                'description': description,
                'created_at': now
            }
        )


def reverse_traits(apps, schema_editor):
    """Supprime les traits si on revient en arrière"""
    PersonalityTrait = apps.get_model('gamification', 'PersonalityTrait')
    PersonalityTrait.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('gamification', '0001_initial'),  # Change le numéro selon ta dernière migration
    ]

    operations = [
        migrations.RunPython(load_traits, reverse_traits),
    ]