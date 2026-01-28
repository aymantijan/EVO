from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from .models import (
    UserProfile, Skill, UserSkill, Achievement, UserAchievement,
    Challenge, UserChallenge, StudySession, Action, PersonalityTrait,
    UserPersonalityTrait, ActivityEvaluation, EvaluationTraitLink,
    ActivityArtifact, Resource
)

# ============================================================================
# CONSTANTS & UTILITIES
# ============================================================================

# Couleurs pour 10 galaxies (100 niveaux par galaxie)
GALAXY_COLORS = {
    1: '#10b981',  # Galaxie 1: Vert
    2: '#06b6d4',  # Galaxie 2: Cyan
    3: '#f59e0b',  # Galaxie 3: Orange
    4: '#ec4899',  # Galaxie 4: Rose
    5: '#8b5cf6',  # Galaxie 5: Violet
    6: '#ef4444',  # Galaxie 6: Rouge
    7: '#3b82f6',  # Galaxie 7: Bleu
    8: '#14b8a6',  # Galaxie 8: Teal
    9: '#f97316',  # Galaxie 9: Orange foncé
    10: '#6366f1',  # Galaxie 10: Indigo
}

GALAXY_NAMES = {
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

TYPE_COLORS = {
    'Livre': '#8b5cf6',
    'Article': '#3b82f6',
    'FilmSérie': '#f59e0b',
    'Mentor': '#ec4899',
    'Podcast': '#10b981'
}

DOMAINE_COLORS = {
    'Finance': '#059669',
    'Business': '#2563eb',
    'Mindset': '#dc2626',
    'Tech': '#7c3aed',
    'Entrepreneuriat': '#ea580c',
    'Philosophie': '#6366f1',
    'Physique': '#3b82f6',
    'Chimie': '#8b5cf6',
    'Agriculture': '#10b981',
    'Romans': '#ec4899',
    'Autre': '#6b7280'
}


def get_galaxy_info(level):
    """Retourne la galaxie et le niveau dans la galaxie"""
    galaxy = ((level - 1) // 100) + 1
    level_in_galaxy = ((level - 1) % 100) + 1
    return galaxy, level_in_galaxy


def get_badge_html(text, color):
    """Crée un badge HTML stylisé"""
    return format_html(
        '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">{}</span>',
        color,
        text
    )


def get_progress_bar(percentage):
    """Crée une barre de progression"""
    return format_html(
        '<div style="width: 100px; height: 20px; background: #e5e7eb; border-radius: 10px; overflow: hidden; display: inline-block;">'
        '<div style="width: {}%; height: 100%; background: linear-gradient(90deg, #10b981, #06b6d4); display: flex; align-items: center; justify-content: center; color: white; font-size: 11px; font-weight: bold;">{}%</div>'
        '</div>',
        percentage,
        percentage
    )


# ============================================================================
# RESOURCE ADMIN
# ============================================================================

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'type_badge', 'domaine_badge', 'niveau_galaxy_badge', 'is_active_display',
                    'created_at')
    list_filter = ('type', 'domaine', 'niveau', 'is_active', 'created_at')
    search_fields = ('titre', 'auteur', 'description')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('📚 Informations Principales', {
            'fields': ('titre', 'auteur', 'description')
        }),
        ('📂 Classification', {
            'fields': ('type', 'domaine', 'niveau')
        }),
        ('🔗 Ressource', {
            'fields': ('url', 'image')
        }),
        ('⚙️ Paramètres', {
            'fields': ('is_active',)
        }),
        ('📅 Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def type_badge(self, obj):
        return get_badge_html(obj.type, TYPE_COLORS.get(obj.type, '#666'))

    type_badge.short_description = 'Type'

    def domaine_badge(self, obj):
        return get_badge_html(obj.domaine, DOMAINE_COLORS.get(obj.domaine, '#666'))

    domaine_badge.short_description = 'Domaine'

    def niveau_galaxy_badge(self, obj):
        galaxy, level_in_galaxy = get_galaxy_info(obj.niveau)
        galaxy_name = GALAXY_NAMES.get(galaxy, 'Galaxie Inconnue')
        color = GALAXY_COLORS.get(galaxy, '#666')
        text = f'{galaxy_name} / Niv. {level_in_galaxy}'
        return get_badge_html(text, color)

    niveau_galaxy_badge.short_description = 'Niveau'

    def is_active_display(self, obj):
        color = '#10b981' if obj.is_active else '#ef4444'
        text = '✅ Actif' if obj.is_active else '❌ Inactif'
        return get_badge_html(text, color)

    is_active_display.short_description = 'Statut'


# ============================================================================
# USER PROFILE ADMIN
# ============================================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'level_galaxy_badge', 'experience_points', 'total_points', 'badges_count', 'updated_at']
    list_filter = ['level', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ('created_at', 'updated_at', 'galaxy_info')

    fieldsets = (
        ('👤 Utilisateur', {
            'fields': ('user',)
        }),
        ('🌌 Galaxie & Niveau', {
            'fields': ('level', 'galaxy_info')
        }),
        ('⭐ Statistiques', {
            'fields': ('experience_points', 'total_points', 'badges_count')
        }),
        ('📅 Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def level_galaxy_badge(self, obj):
        galaxy = obj.galaxy
        level_in_galaxy = obj.level_in_galaxy
        galaxy_name = GALAXY_NAMES.get(galaxy, 'Galaxie Inconnue')
        color = GALAXY_COLORS.get(galaxy, '#666')
        text = f'{galaxy_name} / Lvl {level_in_galaxy}'
        return get_badge_html(text, color)

    level_galaxy_badge.short_description = 'Niveau'

    def galaxy_info(self, obj):
        galaxy = obj.galaxy
        level_in_galaxy = obj.level_in_galaxy
        galaxy_name = GALAXY_NAMES.get(galaxy, 'Galaxie Inconnue')

        info_text = f"""
        <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; font-family: monospace;">
            <p><strong>Niveau Global:</strong> {obj.level}/1000</p>
            <p><strong>Galaxie:</strong> {galaxy}/10 - {galaxy_name}</p>
            <p><strong>Niveau dans Galaxie:</strong> {level_in_galaxy}/100</p>
            <p style="margin-top: 10px; color: #6b7280;">
                Galaxies: Niv. 1-100 (Galaxy 1), 101-200 (Galaxy 2), etc...
            </p>
        </div>
        """
        return format_html(info_text)

    galaxy_info.short_description = 'Informations Galaxie'


# ============================================================================
# SKILL & USER SKILL ADMIN
# ============================================================================

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'skill_icon', 'skill_color', 'users_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ('created_at',)

    fieldsets = (
        ('📝 Informations', {
            'fields': ('name', 'description')
        }),
        ('🎨 Apparence', {
            'fields': ('icon', 'color')
        }),
        ('📅 Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def skill_icon(self, obj):
        return format_html('<span style="font-size: 24px;">{}</span>', obj.icon)

    skill_icon.short_description = 'Icône'

    def skill_color(self, obj):
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 5px; border: 2px solid #d1d5db;"></div>',
            obj.color
        )

    skill_color.short_description = 'Couleur'

    def users_count(self, obj):
        count = obj.gamification_users.count()
        return get_badge_html(f'{count} utilisateurs', '#3b82f6')

    users_count.short_description = 'Utilisateurs'


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'level', 'mastery_bar', 'experience', 'updated_at']
    list_filter = ['skill', 'level']
    search_fields = ['user__username', 'skill__name']
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('👤 Utilisateur & Compétence', {
            'fields': ('user', 'skill')
        }),
        ('📊 Progression', {
            'fields': ('level', 'experience', 'mastery_percentage')
        }),
        ('📅 Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def mastery_bar(self, obj):
        return get_progress_bar(obj.mastery_percentage)

    mastery_bar.short_description = 'Maîtrise'


# ============================================================================
# ACHIEVEMENT ADMIN
# ============================================================================

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'achievement_icon', 'category_badge', 'xp_reward', 'users_count', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ('created_at',)

    fieldsets = (
        ('🏆 Informations', {
            'fields': ('name', 'description')
        }),
        ('📂 Classification', {
            'fields': ('category', 'icon')
        }),
        ('⚙️ Paramètres', {
            'fields': ('requirement_type', 'requirement_value', 'xp_reward')
        }),
        ('📅 Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def achievement_icon(self, obj):
        return format_html('<span style="font-size: 24px;">{}</span>', obj.icon)

    achievement_icon.short_description = 'Icône'

    def category_badge(self, obj):
        colors = {
            'combat': '#ef4444',
            'exploration': '#f59e0b',
            'social': '#ec4899',
            'learning': '#3b82f6',
            'challenge': '#10b981',
        }
        return get_badge_html(obj.get_category_display(), colors.get(obj.category, '#666'))

    category_badge.short_description = 'Catégorie'

    def users_count(self, obj):
        count = obj.gamification_users.count()
        return get_badge_html(f'{count} débloqués', '#8b5cf6')

    users_count.short_description = 'Déverrouillages'


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'unlocked_date', 'days_ago']
    list_filter = ['achievement__category', 'unlocked_at']
    search_fields = ['user__username', 'achievement__name']
    readonly_fields = ('unlocked_at',)

    fieldsets = (
        ('🏆 Déblocage', {
            'fields': ('user', 'achievement', 'unlocked_at')
        }),
    )

    def unlocked_date(self, obj):
        return obj.unlocked_at.strftime('%d/%m/%Y %H:%M')

    unlocked_date.short_description = 'Date de déblocage'

    def days_ago(self, obj):
        delta = now() - obj.unlocked_at
        days = delta.days
        if days == 0:
            return '🔥 Aujourd\'hui'
        elif days == 1:
            return '⏰ Hier'
        else:
            return f'📅 Il y a {days} jours'

    days_ago.short_description = 'Récemment'


# ============================================================================
# CHALLENGE ADMIN
# ============================================================================

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty_badge', 'status_display', 'xp_reward', 'participants_count', 'start_date']
    list_filter = ['difficulty', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at',)

    fieldsets = (
        ('📋 Informations', {
            'fields': ('title', 'description')
        }),
        ('⚙️ Paramètres', {
            'fields': ('difficulty', 'challenge_type', 'target_value', 'xp_reward')
        }),
        ('📅 Durée', {
            'fields': ('start_date', 'end_date')
        }),
        ('📅 Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def difficulty_badge(self, obj):
        colors = {
            'easy': '#10b981',
            'medium': '#f59e0b',
            'hard': '#ef4444',
            'extreme': '#8b5cf6'
        }
        return get_badge_html(obj.get_difficulty_display(), colors.get(obj.difficulty, '#666'))

    difficulty_badge.short_description = 'Difficulté'

    def status_display(self, obj):
        if now() < obj.start_date:
            return get_badge_html('⏳ Pas commencé', '#9ca3af')
        elif now() > obj.end_date:
            return get_badge_html('✅ Terminé', '#10b981')
        else:
            return get_badge_html('🔴 En cours', '#ef4444')

    status_display.short_description = 'Statut'

    def participants_count(self, obj):
        count = obj.gamification_users_challenges.count()
        return get_badge_html(f'{count} participants', '#06b6d4')

    participants_count.short_description = 'Participants'


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'status_badge', 'progress_bar', 'completion_rate', 'completed_at']
    list_filter = ['status', 'challenge__difficulty']
    search_fields = ['user__username', 'challenge__title']
    readonly_fields = ('completed_at',)

    fieldsets = (
        ('👤 Utilisateur & Défi', {
            'fields': ('user', 'challenge')
        }),
        ('📊 Progression', {
            'fields': ('status', 'progress')
        }),
        ('✅ Completion', {
            'fields': ('completed_at',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'active': '#f59e0b',
            'completed': '#10b981',
            'failed': '#ef4444'
        }
        return get_badge_html(obj.get_status_display(), colors.get(obj.status, '#666'))

    status_badge.short_description = 'Statut'

    def progress_bar(self, obj):
        return get_progress_bar(obj.progress)

    progress_bar.short_description = 'Progression'

    def completion_rate(self, obj):
        return f'{obj.progress}%'

    completion_rate.short_description = 'Taux'


# ============================================================================
# STUDY SESSION ADMIN - ✅ CORRIGÉ
# ============================================================================

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'title', 'duration_minutes', 'points_earned', 'started_at_display',
                    'session_quality']
    list_filter = ['skill', 'started_at']
    search_fields = ['user__username', 'title', 'notes']
    date_hierarchy = 'started_at'
    readonly_fields = ('started_at',)

    fieldsets = (
        ('📚 Session', {
            'fields': ('user', 'skill', 'title')
        }),
        ('⏱️ Durée', {
            'fields': ('started_at', 'duration_minutes')
        }),
        ('⭐ Résultats', {
            'fields': ('points_earned',)
        }),
        ('📝 Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def started_at_display(self, obj):
        return obj.started_at.strftime('%d/%m %H:%M')

    started_at_display.short_description = 'Début'

    def session_quality(self, obj):
        quality_score = min(100, (obj.points_earned / 100) * 100) if obj.points_earned else 0

        if quality_score >= 80:
            color = '#10b981'
            label = '⭐⭐⭐ Excellent'
        elif quality_score >= 60:
            color = '#f59e0b'
            label = '⭐⭐ Bon'
        else:
            color = '#ef4444'
            label = '⭐ Acceptable'

        return get_badge_html(label, color)

    session_quality.short_description = 'Qualité'


# ============================================================================
# ACTION ADMIN
# ============================================================================

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type_badge', 'points', 'created_at_display']
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('👤 Action', {
            'fields': ('user', 'action_type', 'description')
        }),
        ('⭐ Récompense', {
            'fields': ('points',)
        }),
        ('📅 Date', {
            'fields': ('created_at',)
        }),
    )

    def action_type_badge(self, obj):
        colors = {
            'study': '#3b82f6',
            'quiz': '#10b981',
            'project': '#f59e0b',
            'comment': '#ec4899',
            'help': '#06b6d4',
            'streak': '#8b5cf6',
        }
        return get_badge_html(obj.get_action_type_display(), colors.get(obj.action_type, '#666'))

    action_type_badge.short_description = 'Type'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')

    created_at_display.short_description = 'Date'


# ============================================================================
# PERSONALITY TRAIT ADMIN
# ============================================================================

@admin.register(PersonalityTrait)
class PersonalityTraitAdmin(admin.ModelAdmin):
    list_display = ['name', 'trait_icon', 'category_badge', 'is_negative_display', 'users_count', 'created_at']
    list_filter = ['category', 'is_negative', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ('created_at',)

    fieldsets = (
        ('🧠 Trait', {
            'fields': ('name', 'description')
        }),
        ('📂 Classification', {
            'fields': ('category', 'is_negative')
        }),
        ('🎨 Apparence', {
            'fields': ('icon',)
        }),
        ('📅 Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def trait_icon(self, obj):
        return format_html('<span style="font-size: 24px;">{}</span>', obj.icon if obj.icon else '—')

    trait_icon.short_description = 'Icône'

    def category_badge(self, obj):
        colors = {
            'cognitive': '#3b82f6',
            'emotional': '#f59e0b',
            'behavioral': '#10b981',
            'social': '#ec4899',
            'moral': '#6366f1',
            'dark': '#6b7280',
            'motivational': '#06b6d4',
            'existential': '#8b5cf6',
            'leadership': '#059669',
            'affective': '#dc2626',
        }
        return get_badge_html(obj.get_category_display(), colors.get(obj.category, '#666'))

    category_badge.short_description = 'Catégorie'

    def is_negative_display(self, obj):
        color = '#ef4444' if obj.is_negative else '#10b981'
        text = '⚠️ Négatif' if obj.is_negative else '✅ Positif'
        return get_badge_html(text, color)

    is_negative_display.short_description = 'Type'

    def users_count(self, obj):
        count = obj.gamification_user_stats.count()
        return get_badge_html(f'{count} users', '#8b5cf6')

    users_count.short_description = 'Utilisateurs'


@admin.register(UserPersonalityTrait)
class UserPersonalityTraitAdmin(admin.ModelAdmin):
    list_display = ['user', 'trait', 'hp_display', 'hp_bar', 'updated_at_display']
    list_filter = ['trait__category', 'updated_at']
    search_fields = ['user__username', 'trait__name']
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('🧠 Trait de personnalité', {
            'fields': ('user', 'trait')
        }),
        ('❤️ Points de vie', {
            'fields': ('hp',)
        }),
        ('📅 Date', {
            'fields': ('updated_at',)
        }),
    )

    def hp_display(self, obj):
        return get_badge_html(f'❤️ {obj.hp} HP', '#ef4444')

    hp_display.short_description = 'HP'

    def hp_bar(self, obj):
        max_hp = 100
        percentage = (obj.hp / max_hp) * 100
        return get_progress_bar(int(percentage))

    hp_bar.short_description = 'Barre de vie'

    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%d/%m/%Y %H:%M')

    updated_at_display.short_description = 'Mise à jour'


# ============================================================================
# ACTIVITY EVALUATION ADMIN
# ============================================================================

@admin.register(ActivityEvaluation)
class ActivityEvaluationAdmin(admin.ModelAdmin):
    list_display = ['user', 'quality_score_display', 'xp_awarded', 'is_valid_display', 'created_at_display',
                    'evaluation_quality']
    list_filter = ['is_valid', 'created_at', 'quality_score']
    search_fields = ['user__username', 'description', 'ai_feedback']
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('📋 Évaluation', {
            'fields': ('user', 'description')
        }),
        ('🤖 IA', {
            'fields': ('ai_feedback',)
        }),
        ('📊 Résultats', {
            'fields': ('quality_score', 'xp_awarded', 'is_valid')
        }),
        ('📈 Artefacts Détectés', {
            'fields': ('books_read', 'academic_articles', 'projects_worked', 'online_courses', 'social_contributions',
                       'networking_events'),
            'classes': ('collapse',)
        }),
        ('📅 Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def quality_score_display(self, obj):
        color = '#10b981' if obj.quality_score >= 75 else '#f59e0b' if obj.quality_score >= 50 else '#ef4444'
        return get_badge_html(f'{obj.quality_score:.1f}/100', color)

    quality_score_display.short_description = 'Score'

    def is_valid_display(self, obj):
        color = '#10b981' if obj.is_valid else '#ef4444'
        text = '✅ Valide' if obj.is_valid else '❌ Rejeté'
        return get_badge_html(text, color)

    is_valid_display.short_description = 'Validation'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')

    created_at_display.short_description = 'Date'

    def evaluation_quality(self, obj):
        if obj.quality_score >= 85:
            return '⭐⭐⭐ Excellent'
        elif obj.quality_score >= 70:
            return '⭐⭐ Bon'
        elif obj.quality_score >= 50:
            return '⭐ Acceptable'
        else:
            return '❌ Faible'

    evaluation_quality.short_description = 'Qualité'


# ============================================================================
# EVALUATION TRAIT LINK ADMIN
# ============================================================================

@admin.register(EvaluationTraitLink)
class EvaluationTraitLinkAdmin(admin.ModelAdmin):
    list_display = ['evaluation', 'trait', 'hp_awarded_display', 'relevance_preview', 'created_at_display']
    list_filter = ['trait__category']
    search_fields = ['evaluation__id', 'trait__name']
    readonly_fields = ('evaluation', 'trait')

    fieldsets = (
        ('🔗 Lien', {
            'fields': ('evaluation', 'trait')
        }),
        ('❤️ Récompense', {
            'fields': ('hp_awarded',)
        }),
        ('📝 Pertinence', {
            'fields': ('relevance',)
        }),
    )

    def hp_awarded_display(self, obj):
        return get_badge_html(f'❤️ +{obj.hp_awarded} HP', '#ef4444')

    hp_awarded_display.short_description = 'HP Attribué'

    def relevance_preview(self, obj):
        preview = obj.relevance[:50] if obj.relevance else 'N/A'
        return preview + ('...' if len(obj.relevance or '') > 50 else '')

    relevance_preview.short_description = 'Pertinence'

    def created_at_display(self, obj):
        return obj.evaluation.created_at.strftime('%d/%m/%Y %H:%M')

    created_at_display.short_description = 'Date'


# ============================================================================
# ACTIVITY ARTIFACT ADMIN
# ============================================================================

@admin.register(ActivityArtifact)
class ActivityArtifactAdmin(admin.ModelAdmin):
    list_display = ['name', 'artifact_type_badge', 'evaluation', 'url_display', 'created_at_display']
    list_filter = ['artifact_type', 'created_at']
    search_fields = ['name', 'description', 'evaluation__id']
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('📦 Artifact', {
            'fields': ('name', 'description')
        }),
        ('📂 Classification', {
            'fields': ('artifact_type', 'evaluation')
        }),
        ('🔗 Ressource', {
            'fields': ('url',)
        }),
        ('📅 Date', {
            'fields': ('created_at',)
        }),
    )

    def artifact_type_badge(self, obj):
        colors = {
            'book': '#8b5cf6',
            'article': '#3b82f6',
            'project': '#f59e0b',
            'course': '#10b981',
            'contribution': '#ec4899',
            'event': '#06b6d4',
        }
        return get_badge_html(obj.get_artifact_type_display(), colors.get(obj.artifact_type, '#666'))

    artifact_type_badge.short_description = 'Type'

    def url_display(self, obj):
        if obj.url:
            return format_html(
                '<a href="{}" target="_blank" style="color: #3b82f6; text-decoration: underline;">🔗 Voir</a>',
                obj.url
            )
        return '—'

    url_display.short_description = 'URL'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')

    created_at_display.short_description = 'Date'


# ============================================================================
# ADMIN SITE CONFIGURATION
# ============================================================================

admin.site.site_header = "⚡ Admin Gamification Life - 1000 Levels / 10 Galaxies"
admin.site.site_title = "Admin Gamification"
admin.site.index_title = "Bienvenue sur le panneau d'administration"