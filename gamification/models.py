from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


# ==================== USER PROFILE ====================

class UserProfile(models.Model):
    """Profil utilisateur étendu avec gamification - 1000 niveaux / 10 galaxies"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gamification_profile')
    level = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(1000)])
    experience_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    badges_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    # ✅ AJOUTER LES 3 JSONFIELD
    profile_image = models.ImageField(upload_to='profiles/images/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='profiles/covers/', null=True, blank=True)
    acquired_skills = models.JSONField(default=list, blank=True)
    discovered_categories = models.JSONField(default=list, blank=True)
    explored_domains = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"
        ordering = ['-experience_points']
        indexes = [
            models.Index(fields=['-experience_points']),
            models.Index(fields=['level']),
        ]

    @property
    def galaxy(self):
        """Retourne la galaxie (1-10)"""
        return ((self.level - 1) // 100) + 1

    @property
    def level_in_galaxy(self):
        """Retourne le niveau dans la galaxie (1-100)"""
        return ((self.level - 1) % 100) + 1

    @property
    def galaxy_name(self):
        """Retourne le nom de la galaxie"""
        galaxy_names = {
            1: '🌟 Étoile du Matin',
            2: '💫 Andromède',
            3: '⭐ Voie Lactée',
            4: '🌌 Sombrero',
            5: '🪐 Spirale du Cygne',
            6: '🔴 Nébuleuse du Crabe',
            7: '🔵 Galaxie d\'Orion',
            8: '💎 Trésor Cosmique',
            9: '🌠 Paradis Stellaire',
            10: '👑 Univers Suprême',
        }
        return galaxy_names.get(self.galaxy, 'Galaxie Inconnue')

    def __str__(self):
        return f"{self.user.username} - Level {self.level} ({self.galaxy_name})"


# ==================== SKILL ====================

class Skill(models.Model):
    """Compétences/Domaines d'apprentissage"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='📚')
    color = models.CharField(max_length=7, default='#3498db')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"
        ordering = ['name']

    def __str__(self):
        return self.name


# ==================== USER SKILL ====================

class UserSkill(models.Model):
    """Progression utilisateur dans une compétence"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_user_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='gamification_users')
    level = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    experience = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    mastery_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Compétence Utilisateur"
        verbose_name_plural = "Compétences Utilisateurs"
        unique_together = ['user', 'skill']
        ordering = ['-experience']

    def __str__(self):
        return f"{self.user.username} - {self.skill.name} (Level {self.level})"


# ==================== ACHIEVEMENT ====================

class Achievement(models.Model):
    """Accomplissements/Badges que les utilisateurs peuvent débloquer"""
    CATEGORY_CHOICES = [
        ('combat', 'Combat'),
        ('exploration', 'Exploration'),
        ('social', 'Social'),
        ('learning', 'Learning'),
        ('challenge', 'Challenge'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    icon = models.CharField(max_length=50, default='🏆')
    requirement_type = models.CharField(max_length=50)
    requirement_value = models.IntegerField()
    xp_reward = models.IntegerField(default=50, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Accomplissement"
        verbose_name_plural = "Accomplissements"
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


# ==================== USER ACHIEVEMENT ====================

class UserAchievement(models.Model):
    """Suivi des accomplissements débloqués par les utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_achievements_unlocked')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='gamification_users')
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Accomplissement Utilisateur"
        verbose_name_plural = "Accomplissements Utilisateurs"
        unique_together = ['user', 'achievement']
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


# ==================== CHALLENGE ====================

class Challenge(models.Model):
    """Défis hebdomadaires/mensuels"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('extreme', 'Extreme'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    challenge_type = models.CharField(max_length=50)
    target_value = models.IntegerField(validators=[MinValueValidator(1)])
    xp_reward = models.IntegerField(default=100, validators=[MinValueValidator(0)])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Défi"
        verbose_name_plural = "Défis"
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        """Vérifie si le défi est actuellement actif"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date


# ==================== USER CHALLENGE ====================

class UserChallenge(models.Model):
    """Suivi de la progression utilisateur sur les défis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_challenges')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='gamification_users_challenges')
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='active'
    )
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Défi Utilisateur"
        verbose_name_plural = "Défis Utilisateurs"
        unique_together = ['user', 'challenge']
        ordering = ['-challenge__start_date']

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"


# ==================== STUDY SESSION ====================

class StudySession(models.Model):
    """Sessions d'étude"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_study_sessions')
    skill = models.ForeignKey(
        Skill,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gamification_study_sessions'
    )
    title = models.CharField(max_length=200)
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)])
    points_earned = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True)
    started_at = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Session d'Étude"
        verbose_name_plural = "Sessions d'Étude"
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


# ==================== ACTION ====================

class Action(models.Model):
    """Actions/Activités des utilisateurs pour la gamification"""
    ACTION_TYPES = [
        ('study', 'Study Session'),
        ('quiz', 'Quiz Completed'),
        ('project', 'Project Submission'),
        ('comment', 'Community Comment'),
        ('help', 'Help Given'),
        ('streak', 'Study Streak'),
        ('quotidien', 'Activité Quotidienne'),
        ('day_validated', 'Journée Validée'),
        ('ia_evaluation', 'Évaluation IA'),
        ('time_block', 'Time Block'),
        ('time_block_toggled', 'Time Block Toggled'),
        ('evaluation_confirmed', 'Evaluation Confirmed'),
        ('challenge', 'Challenge'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_actions')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField(blank=True)
    points = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Action"
        verbose_name_plural = "Actions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action_type}"


# ==================== PERSONALITY TRAIT ====================

class PersonalityTrait(models.Model):
    """Traits de personnalité catégorisés (102 traits uniques)"""
    CATEGORY_CHOICES = [
        ('cognitive', 'Cognitif'),
        ('emotional', 'Émotionnel'),
        ('behavioral', 'Comportemental'),
        ('social', 'Social'),
        ('moral', 'Moral/Éthique'),
        ('dark', 'Traits Sombres'),
        ('motivational', 'Motivationnel'),
        ('existential', 'Existentiel'),
        ('leadership', 'Leadership'),
        ('affective', 'Affectif'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='behavioral')
    is_negative = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Trait de Personnalité"
        verbose_name_plural = "Traits de Personnalité"
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_negative']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


# ==================== USER PERSONALITY TRAIT ====================

class UserPersonalityTrait(models.Model):
    """HP des traits de personnalité par utilisateur"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_personality_traits')
    trait = models.ForeignKey(PersonalityTrait, on_delete=models.CASCADE, related_name='gamification_user_stats')
    hp = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Trait de Personnalité Utilisateur"
        verbose_name_plural = "Traits de Personnalité Utilisateurs"
        unique_together = ('user', 'trait')
        ordering = ['-hp']
        indexes = [
            models.Index(fields=['user', '-hp']),
            models.Index(fields=['trait']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.trait.name}: {self.hp}HP"


# ==================== ACTIVITY EVALUATION ====================

class ActivityEvaluation(models.Model):
    """Stocke CHAQUE évaluation d'activité (3 sections: Quotidien, Planning, IA)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_activity_evaluations')
    description = models.TextField()
    is_valid = models.BooleanField(default=True)
    xp_awarded = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    quality_score = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    ai_feedback = models.TextField()

    # Détections (Section 3 - IA)
    books_read = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    academic_articles = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    projects_worked = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    online_courses = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    social_contributions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    networking_events = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Évaluation d'Activité"
        verbose_name_plural = "Évaluations d'Activité"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')} (+{self.xp_awarded}XP)"


# ==================== EVALUATION TRAIT LINK ====================

class EvaluationTraitLink(models.Model):
    """Lien entre une évaluation et les traits détectés/attribués"""
    evaluation = models.ForeignKey(ActivityEvaluation, on_delete=models.CASCADE,
                                   related_name='gamification_detected_traits')
    trait = models.ForeignKey(PersonalityTrait, on_delete=models.CASCADE, related_name='gamification_evaluations')
    hp_awarded = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    relevance = models.TextField()

    class Meta:
        verbose_name = "Lien Évaluation-Trait"
        verbose_name_plural = "Liens Évaluation-Traits"
        unique_together = ('evaluation', 'trait')
        indexes = [
            models.Index(fields=['evaluation']),
            models.Index(fields=['trait']),
        ]

    def __str__(self):
        return f"Éval #{self.evaluation.id} - {self.trait.name} (+{self.hp_awarded}HP)"


# ==================== ACTIVITY ARTIFACT ====================

class ActivityArtifact(models.Model):
    """Artefacts détectés (livres, articles, projets, etc) - Section 3 (IA)"""
    ARTIFACT_TYPES = [
        ('book', 'Livre'),
        ('article', 'Article Académique'),
        ('project', 'Projet'),
        ('course', 'Cours en Ligne'),
        ('contribution', 'Contribution Sociale'),
        ('event', 'Événement Réseau'),
    ]

    evaluation = models.ForeignKey(ActivityEvaluation, on_delete=models.CASCADE, related_name='gamification_artifacts')
    artifact_type = models.CharField(max_length=20, choices=ARTIFACT_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Artefact d'Activité"
        verbose_name_plural = "Artefacts d'Activité"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['evaluation']),
            models.Index(fields=['artifact_type']),
        ]

    def __str__(self):
        return f"{self.get_artifact_type_display()} - {self.name}"


# ==================== RESOURCE ====================

class Resource(models.Model):
    """Ressources d'apprentissage accessibles selon le niveau (1-1000)"""
    TYPES = [
        ('Livre', 'Livre'),
        ('Article', 'Article'),
        ('FilmSérie', 'Film/Série'),
        ('Mentor', 'Mentor'),
        ('Podcast', 'Podcast'),
    ]

    DOMAINES = [
        ('Finance', 'Finance'),
        ('Business', 'Business'),
        ('Mindset', 'Mindset'),
        ('Tech', 'Tech'),
        ('Entrepreneuriat', 'Entrepreneuriat'),
        ('Philosophie', 'Philosophie'),
        ('Physique', 'Physique'),
        ('Chimie', 'Chimie'),
        ('Agriculture', 'Agriculture'),
        ('Romans', 'Romans'),
        ('Autre', 'Autre'),
    ]

    titre = models.CharField(max_length=255, verbose_name="Titre")
    auteur = models.CharField(max_length=255, verbose_name="Auteur/Source")
    type = models.CharField(max_length=20, choices=TYPES, default='Livre', verbose_name="Type")
    domaine = models.CharField(max_length=50, choices=DOMAINES, default='Autre', verbose_name="Domaine")
    description = models.TextField(verbose_name="Description", blank=True)
    niveau = models.IntegerField(
        default=1,
        verbose_name="Niveau d'accès minimum",
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text="Niveau requis pour accéder (1-1000)"
    )
    url = models.URLField(blank=True, null=True, verbose_name="URL")
    image = models.URLField(blank=True, null=True, verbose_name="Image")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Ressource"
        verbose_name_plural = "Ressources"
        indexes = [
            models.Index(fields=['niveau', 'domaine']),
            models.Index(fields=['type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.titre} - Niveau {self.niveau}"

    @property
    def galaxy(self):
        """Retourne la galaxie requise (1-10)"""
        return ((self.niveau - 1) // 100) + 1

    @property
    def level_in_galaxy(self):
        """Retourne le niveau dans la galaxie (1-100)"""
        return ((self.niveau - 1) % 100) + 1


class StudySubject(models.Model):
    """Matière dans le Study Tracker"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_study_subjects')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Matière (Study Tracker)"
        verbose_name_plural = "Matières (Study Tracker)"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class StudyChapter(models.Model):
    """Chapitre dans une matière du Study Tracker"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_study_chapters')
    subject = models.ForeignKey(StudySubject, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    coefficient = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chapitre (Study Tracker)"
        verbose_name_plural = "Chapitres (Study Tracker)"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.subject.name} > {self.title}"


class StudySection(models.Model):
    """Section dans un chapitre du Study Tracker"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_study_sections')
    subject = models.ForeignKey(StudySubject, on_delete=models.CASCADE, related_name='sections')
    chapter = models.ForeignKey(StudyChapter, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    progress = models.IntegerField(default=0)  # 0–100
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Section (Study Tracker)"
        verbose_name_plural = "Sections (Study Tracker)"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.chapter.title} > {self.title} ({self.progress}%)"
