from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User


# ====== CLASS BASED VIEWS ======

class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view"""
    template_name = 'dashboard.html'
    login_url = 'login'


class ActionsView(LoginRequiredMixin, TemplateView):
    """Actions view"""
    template_name = 'actions.html'
    login_url = 'login'


class AchievementsView(LoginRequiredMixin, TemplateView):
    """Achievements view"""
    template_name = 'achievements.html'
    login_url = 'login'


class ChallengesView(LoginRequiredMixin, TemplateView):
    """Challenges view"""
    template_name = 'challenges.html'
    login_url = 'login'


class StudyTrackerView(LoginRequiredMixin, TemplateView):
    """Study tracker view"""
    template_name = 'study_tracker.html'
    login_url = 'login'


class ProfileView(LoginRequiredMixin, TemplateView):
    """Profile view"""
    template_name = 'profile.html'
    login_url = 'login'


class SettingsView(LoginRequiredMixin, TemplateView):
    """Settings view"""
    template_name = 'settings.html'
    login_url = 'login'


class LeaderboardView(LoginRequiredMixin, TemplateView):
    """Leaderboard view"""
    template_name = 'leaderboard.html'
    login_url = 'login'


class SkillsView(LoginRequiredMixin, TemplateView):
    """Skills page view"""
    template_name = 'skills_page.html'
    login_url = 'login'


# ====== FUNCTION BASED VIEWS ======

@login_required(login_url='login')
def index(request):
    """Home/Index view"""
    return render(request, 'index.html')


@login_required(login_url='login')
def skills_page(request):
    """Affiche la page complète des compétences"""
    context = {'page_title': 'Mes Compétences'}
    return render(request, 'skills_page.html', context)


# ====== SKILLS API ENDPOINTS ======

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_skills(request):
    """API pour récupérer les compétences de l'utilisateur"""
    try:
        from .models import UserProfile, UserSkill, Skill

        user_profile = UserProfile.objects.get(user=request.user)
        user_skills = UserSkill.objects.filter(user=request.user).select_related('skill')

        user_skills_dict = {us.skill.id: us.progress_percent for us in user_skills}
        all_skills = Skill.objects.all()

        skills_by_domain = {}
        for skill in all_skills:
            domain = skill.domain or 'Autre'
            if domain not in skills_by_domain:
                skills_by_domain[domain] = []

            progress = user_skills_dict.get(skill.id, 0)
            skills_by_domain[domain].append({
                'id': skill.id,
                'name': skill.name,
                'domain': domain,
                'icon': skill.icon or '🎖️',
                'progress_percent': progress,
                'is_unlocked': progress > 0,
                'xp_required': skill.xp_required or 0,
            })

        return Response({
            'status': 'success',
            'skills_by_domain': skills_by_domain,
            'total_unlocked': len([s for s in user_skills_dict.values() if s > 0])
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_skill_details(request, skill_id):
    """API pour récupérer les détails d'une compétence"""
    try:
        from .models import UserSkill, Skill

        skill = Skill.objects.get(id=skill_id)
        user_skill = UserSkill.objects.filter(user=request.user, skill=skill).first()

        progress = user_skill.progress_percent if user_skill else 0

        return Response({
            'status': 'success',
            'skill': {
                'id': skill.id,
                'name': skill.name,
                'description': skill.description or '',
                'domain': skill.domain,
                'icon': skill.icon or '🎖️',
                'progress_percent': progress,
                'is_unlocked': progress > 0,
                'xp_required': skill.xp_required or 0,
            }
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_domain_progress(request, domain):
    """API pour la progression par domaine"""
    try:
        from .models import UserProfile, UserSkill

        user_profile = UserProfile.objects.get(user=request.user)
        user_skills = UserSkill.objects.filter(user=request.user).select_related('skill')
        domain_skills = user_skills.filter(skill__domain=domain)

        if not domain_skills.exists():
            return Response({
                'status': 'error',
                'message': f'Aucune compétence pour: {domain}'
            }, status=404)

        avg_progress = domain_skills.aggregate(avg=Avg('progress_percent'))['avg'] or 0

        return Response({
            'status': 'success',
            'domain': domain,
            'total_skills': domain_skills.count(),
            'average_progress': round(avg_progress, 1),
            'unlocked_count': domain_skills.filter(progress_percent__gt=0).count(),
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


# ====== PROFILE API ENDPOINTS ======

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """API pour récupérer le profil utilisateur"""
    try:
        from .models import UserProfile

        user_profile = UserProfile.objects.get(user=request.user)

        return Response({
            'status': 'success',
            'data': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'total_xp': user_profile.total_xp,
                'level': user_profile.level,
                'weekly_xp': user_profile.weekly_xp if user_profile.weekly_xp else 0,
                'monthly_xp': user_profile.monthly_xp if user_profile.monthly_xp else 0,
                'avatar': user_profile.avatar.url if user_profile.avatar else None,
                'bio': user_profile.bio if user_profile.bio else '',
                'joined_date': request.user.date_joined,
                'last_login': request.user.last_login,
            }
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """API pour mettre à jour le profil"""
    try:
        from .models import UserProfile

        user = request.user
        user_profile = UserProfile.objects.get(user=user)

        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        if 'email' in request.data:
            user.email = request.data['email']
        user.save()

        if 'bio' in request.data:
            user_profile.bio = request.data['bio']
        if 'avatar' in request.FILES:
            user_profile.avatar = request.FILES['avatar']
        user_profile.save()

        return Response({
            'status': 'success',
            'message': 'Profil mis à jour',
            'data': {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'bio': user_profile.bio,
            }
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


# ====== LEADERBOARD API ENDPOINTS ======

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leaderboard(request):
    """API pour le classement global"""
    try:
        from .models import UserProfile
        from .serializers import LeaderboardSerializer

        profiles = UserProfile.objects.select_related('user').order_by('-total_xp')[:1000]
        serializer = LeaderboardSerializer(profiles, many=True)

        return Response({'status': 'success', 'data': serializer.data})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leaderboard_weekly(request):
    """API pour le classement hebdomadaire"""
    try:
        from .models import UserProfile
        from .serializers import LeaderboardSerializer

        profiles = UserProfile.objects.select_related('user').order_by('-weekly_xp')[:100]
        serializer = LeaderboardSerializer(profiles, many=True)

        return Response({'status': 'success', 'data': serializer.data})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leaderboard_monthly(request):
    """API pour le classement mensuel"""
    try:
        from .models import UserProfile
        from .serializers import LeaderboardSerializer

        profiles = UserProfile.objects.select_related('user').order_by('-monthly_xp')[:100]
        serializer = LeaderboardSerializer(profiles, many=True)

        return Response({'status': 'success', 'data': serializer.data})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_rank(request):
    """API pour la position de l'utilisateur"""
    try:
        from .models import UserProfile

        user_profile = UserProfile.objects.get(user=request.user)
        rank = UserProfile.objects.filter(total_xp__gt=user_profile.total_xp).count() + 1

        all_profiles = UserProfile.objects.select_related('user').order_by('-total_xp')
        user_index = list(all_profiles).index(user_profile)
        nearby_profiles = list(all_profiles[max(0, user_index - 2):user_index + 3])

        from .serializers import LeaderboardSerializer
        nearby_serializer = LeaderboardSerializer(nearby_profiles, many=True)

        return Response({
            'status': 'success',
            'data': {
                'current_user': {
                    'username': request.user.username,
                    'total_xp': user_profile.total_xp,
                    'level': user_profile.level,
                    'rank': rank,
                },
                'nearby': nearby_serializer.data
            }
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


# ====== ACHIEVEMENTS API ENDPOINTS ======

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_achievements(request):
    """API pour les achievements"""
    try:
        from .models import UserAchievement, Achievement

        user_achievements = UserAchievement.objects.filter(
            user=request.user
        ).select_related('achievement')

        achievements_data = []
        for ua in user_achievements:
            achievements_data.append({
                'id': ua.achievement.id,
                'name': ua.achievement.name,
                'description': ua.achievement.description,
                'icon': ua.achievement.icon,
                'xp_reward': ua.achievement.xp_reward,
                'unlocked_date': ua.unlocked_date,
                'is_unlocked': ua.is_unlocked,
            })

        return Response({
            'status': 'success',
            'data': achievements_data,
            'total_unlocked': len([a for a in achievements_data if a['is_unlocked']]),
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


# ====== CHALLENGES API ENDPOINTS ======

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_challenges(request):
    """API pour les défis actifs"""
    try:
        from .models import UserChallenge, Challenge

        now = timezone.now()
        user_challenges = UserChallenge.objects.filter(
            user=request.user,
            challenge__start_date__lte=now,
            challenge__end_date__gte=now,
            is_completed=False
        ).select_related('challenge')

        challenges_data = []
        for uc in user_challenges:
            progress_percent = (uc.progress / uc.challenge.target) * 100 if uc.challenge.target > 0 else 0
            challenges_data.append({
                'id': uc.challenge.id,
                'name': uc.challenge.name,
                'description': uc.challenge.description,
                'icon': uc.challenge.icon,
                'target': uc.challenge.target,
                'progress': uc.progress,
                'progress_percent': min(100, progress_percent),
                'xp_reward': uc.challenge.xp_reward,
                'end_date': uc.challenge.end_date,
                'is_completed': uc.is_completed,
            })

        return Response({'status': 'success', 'data': challenges_data})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_challenge(request, challenge_id):
    """API pour compléter un défi"""
    try:
        from .models import UserChallenge, UserProfile, Challenge

        challenge = Challenge.objects.get(id=challenge_id)
        user_challenge = UserChallenge.objects.get(user=request.user, challenge=challenge)

        if not user_challenge.is_completed:
            user_challenge.is_completed = True
            user_challenge.completed_date = timezone.now()
            user_challenge.save()

            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.total_xp += challenge.xp_reward
            user_profile.save()

            return Response({
                'status': 'success',
                'message': f'Défi complété! +{challenge.xp_reward} XP',
                'xp_earned': challenge.xp_reward
            })
        else:
            return Response({'status': 'error', 'message': 'Défi déjà complété'}, status=400)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


# ====== STUDY TRACKER API ENDPOINTS ======

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_study_sessions(request):
    """API pour les sessions d'étude"""
    try:
        from .models import StudySession

        sessions = StudySession.objects.filter(
            user=request.user
        ).order_by('-created_at')[:50]

        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': session.id,
                'title': session.title,
                'duration': session.duration,
                'subject': session.subject,
                'xp_earned': session.xp_earned,
                'created_at': session.created_at,
            })

        return Response({'status': 'success', 'data': sessions_data})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_study_session(request):
    """API pour créer une session d'étude"""
    try:
        from .models import StudySession, UserProfile

        title = request.data.get('title', 'Session d\'étude')
        duration = request.data.get('duration', 30)
        subject = request.data.get('subject', 'Général')

        xp_earned = duration * 10

        session = StudySession.objects.create(
            user=request.user,
            title=title,
            duration=duration,
            subject=subject,
            xp_earned=xp_earned
        )

        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.total_xp += xp_earned
        user_profile.weekly_xp = (user_profile.weekly_xp or 0) + xp_earned
        user_profile.monthly_xp = (user_profile.monthly_xp or 0) + xp_earned
        user_profile.save()

        return Response({
            'status': 'success',
            'message': f'Session créée! +{xp_earned} XP',
            'data': {'session_id': session.id, 'xp_earned': xp_earned}
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


# ====== DASHBOARD API ENDPOINTS ======

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """API pour les stats du dashboard"""
    try:
        from .models import UserProfile, StudySession

        user_profile = UserProfile.objects.get(user=request.user)
        total_study_sessions = StudySession.objects.filter(user=request.user).count()
        total_study_time = sum(
            StudySession.objects.filter(user=request.user).values_list('duration', flat=True)
        ) or 0

        def calculate_level(xp):
            level = 1
            required_xp = 100
            current_xp = xp
            while current_xp >= required_xp:
                current_xp -= required_xp
                level += 1
                required_xp = level * (level + 1) * 50
            return level, current_xp, required_xp

        level, current_xp, required_xp = calculate_level(user_profile.total_xp)

        return Response({
            'status': 'success',
            'data': {
                'total_xp': user_profile.total_xp,
                'level': level,
                'current_xp': current_xp,
                'xp_to_next_level': required_xp,
                'weekly_xp': user_profile.weekly_xp if user_profile.weekly_xp else 0,
                'monthly_xp': user_profile.monthly_xp if user_profile.monthly_xp else 0,
                'total_study_sessions': total_study_sessions,
                'total_study_time': total_study_time,
            }
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


@api_view(['GET'])
def get_leaderboard_simple(request):
    """API simple pour le leaderboard"""
    try:
        from .models import UserProfile

        profiles = UserProfile.objects.select_related('user').order_by('-total_xp')[:100]

        data = []
        for idx, profile in enumerate(profiles, 1):
            data.append({
                'rank': idx,
                'id': profile.user.id,
                'username': profile.user.username,
                'total_xp': profile.total_xp,
                'level': profile.level,
                'weekly_xp': profile.weekly_xp if profile.weekly_xp else 0,
            })

        return Response({'status': 'success', 'data': data})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)
