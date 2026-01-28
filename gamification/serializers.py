from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    UserProfile, Skill, UserSkill, Achievement, UserAchievement,
    Challenge, UserChallenge, StudySession, Action,
    PersonalityTrait, UserPersonalityTrait, ActivityEvaluation,
    EvaluationTraitLink, ActivityArtifact, Resource
)


# ====== USER SERIALIZERS ======

class UserSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle User"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'level', 'experience_points', 'total_points',
            'badges_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['level', 'experience_points', 'total_points', 'badges_count', 'created_at', 'updated_at']


# ====== LEADERBOARD SERIALIZERS ======

class LeaderboardSerializer(serializers.Serializer):
    """Serializer pour le classement"""
    username = serializers.CharField(source='user.username')
    user_id = serializers.SerializerMethodField()
    level = serializers.IntegerField()
    experience_points = serializers.IntegerField()
    total_points = serializers.IntegerField()
    badges_count = serializers.IntegerField()
    rank = serializers.IntegerField()

    def get_user_id(self, obj):
        return obj.user.id


class LeaderboardWeeklySerializer(serializers.Serializer):
    """Serializer pour le classement hebdomadaire"""
    username = serializers.CharField()
    user_id = serializers.IntegerField()
    weekly_points = serializers.IntegerField()
    rank = serializers.IntegerField()


class LeaderboardMonthlySerializer(serializers.Serializer):
    """Serializer pour le classement mensuel"""
    username = serializers.CharField()
    user_id = serializers.IntegerField()
    monthly_points = serializers.IntegerField()
    rank = serializers.IntegerField()


class UserRankSerializer(serializers.Serializer):
    """Serializer pour le classement utilisateur"""
    rank = serializers.IntegerField()
    total_users = serializers.IntegerField()
    percentile = serializers.FloatField()
    experience_points = serializers.IntegerField()


# ====== SKILLS SERIALIZERS ======

class SkillSerializer(serializers.ModelSerializer):
    """Serializer pour les compétences"""

    class Meta:
        model = Skill
        fields = ['id', 'name', 'description', 'icon', 'color', 'created_at']


class UserSkillSerializer(serializers.ModelSerializer):
    """Serializer pour les compétences de l'utilisateur"""
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        source='skill',
        write_only=True,
        required=False
    )

    class Meta:
        model = UserSkill
        fields = ['id', 'skill', 'skill_id', 'level', 'experience', 'mastery_percentage', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SkillDetailsSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les compétences avec progression utilisateur"""
    users = UserSkillSerializer(many=True, read_only=True)

    class Meta:
        model = Skill
        fields = ['id', 'name', 'description', 'icon', 'color', 'users', 'created_at']


class DomainProgressSerializer(serializers.Serializer):
    """Serializer pour la progression par domaine"""
    domain = serializers.CharField()
    total_skills = serializers.IntegerField()
    completed_skills = serializers.IntegerField()
    average_mastery = serializers.FloatField()
    overall_progress = serializers.FloatField()


# ====== ACHIEVEMENT SERIALIZERS ======

class AchievementSerializer(serializers.ModelSerializer):
    """Serializer pour les accomplissements"""

    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description', 'category', 'icon', 'requirement_type', 'requirement_value', 'xp_reward',
                  'created_at']


class UserAchievementSerializer(serializers.ModelSerializer):
    """Serializer pour les accomplissements utilisateur"""
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'unlocked_at']


# ====== CHALLENGE SERIALIZERS ======

class ChallengeSerializer(serializers.ModelSerializer):
    """Serializer pour les défis"""
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = ['id', 'title', 'description', 'difficulty', 'challenge_type', 'target_value', 'xp_reward',
                  'start_date', 'end_date', 'is_active', 'created_at']

    def get_is_active(self, obj):
        """Retourne si le défi est actif"""
        return obj.is_active


class UserChallengeSerializer(serializers.ModelSerializer):
    """Serializer pour la progression utilisateur sur les défis"""
    challenge = ChallengeSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = UserChallenge
        fields = ['id', 'challenge', 'status', 'progress', 'progress_percentage', 'completed_at']

    def get_progress_percentage(self, obj):
        """Calcule le pourcentage de progression"""
        if obj.challenge.target_value == 0:
            return 0
        return min(100, int((obj.progress / obj.challenge.target_value) * 100))


# ====== STUDY SESSION SERIALIZERS ======

class StudySessionSerializer(serializers.ModelSerializer):
    """Serializer pour les sessions d'étude"""
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        source='skill',
        write_only=True,
        required=False
    )

    class Meta:
        model = StudySession
        fields = ['id', 'skill_name', 'skill_id', 'title', 'duration_minutes', 'points_earned', 'notes', 'started_at',
                  'end_time']


# ====== ACTION SERIALIZERS ======

class ActionSerializer(serializers.ModelSerializer):
    """Serializer pour les actions utilisateur"""

    class Meta:
        model = Action
        fields = ['id', 'action_type', 'description', 'points', 'created_at']


# ====== PERSONALITY TRAIT SERIALIZERS ======

class PersonalityTraitSerializer(serializers.ModelSerializer):
    """Serializer pour les traits de personnalité"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = PersonalityTrait
        fields = ['id', 'name', 'description', 'category', 'category_display', 'is_negative', 'created_at']


class UserPersonalityTraitSerializer(serializers.ModelSerializer):
    """Serializer pour les traits de personnalité utilisateur"""
    trait = PersonalityTraitSerializer(read_only=True)
    trait_id = serializers.PrimaryKeyRelatedField(
        queryset=PersonalityTrait.objects.all(),
        source='trait',
        write_only=True,
        required=False
    )

    class Meta:
        model = UserPersonalityTrait
        fields = ['id', 'trait', 'trait_id', 'hp', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# ====== ACTIVITY EVALUATION SERIALIZERS ======

class ActivityEvaluationSerializer(serializers.ModelSerializer):
    """Serializer pour les évaluations d'activité"""

    class Meta:
        model = ActivityEvaluation
        fields = [
            'id', 'user', 'description', 'is_valid', 'xp_awarded',
            'quality_score', 'ai_feedback', 'books_read', 'academic_articles',
            'projects_worked', 'online_courses', 'social_contributions',
            'networking_events', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


# ====== EVALUATION TRAIT LINK SERIALIZER ======

class EvaluationTraitLinkSerializer(serializers.ModelSerializer):
    """Serializer pour les liens entre évaluation et traits"""
    trait = PersonalityTraitSerializer(read_only=True)

    class Meta:
        model = EvaluationTraitLink
        fields = ['id', 'evaluation', 'trait', 'hp_awarded', 'relevance', 'created_at']
        read_only_fields = ['created_at']


# ====== ACTIVITY ARTIFACT SERIALIZER ======

class ActivityArtifactSerializer(serializers.ModelSerializer):
    """Serializer pour les artefacts d'activité"""

    class Meta:
        model = ActivityArtifact
        fields = ['id', 'evaluation', 'artifact_type', 'name', 'description', 'url', 'created_at']
        read_only_fields = ['created_at']


# ====== RESOURCE SERIALIZERS ======

class ResourceSerializer(serializers.ModelSerializer):
    """Serializer pour les ressources d'apprentissage"""

    class Meta:
        model = Resource
        fields = [
            'id', 'titre', 'auteur', 'type', 'domaine',
            'description', 'niveau', 'url', 'image', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResourceDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les ressources"""

    class Meta:
        model = Resource
        fields = [
            'id', 'titre', 'auteur', 'type', 'domaine',
            'description', 'niveau', 'url', 'image', 'is_active',
            'created_at', 'updated_at'
        ]


class ResourceListSerializer(serializers.Serializer):
    """Serializer pour lister les ressources groupées par type"""
    Livre = ResourceSerializer(many=True)
    Article = ResourceSerializer(many=True)
    FilmSérie = ResourceSerializer(many=True)
    Podcast = ResourceSerializer(many=True)
    Mentor = ResourceSerializer(many=True)


# ====== DASHBOARD SERIALIZERS ======

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques du tableau de bord"""
    level = serializers.IntegerField()
    experience_points = serializers.IntegerField()
    total_points = serializers.IntegerField()
    badges_count = serializers.IntegerField()
    active_challenges_count = serializers.IntegerField()
    completed_challenges_count = serializers.IntegerField()
    study_sessions_count = serializers.IntegerField()
    total_study_hours = serializers.FloatField()
    recent_achievements = AchievementSerializer(many=True)
    active_challenges = ChallengeSerializer(many=True)
    top_skills = UserSkillSerializer(many=True)
