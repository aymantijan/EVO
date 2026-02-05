from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta, datetime

import json
import requests
import os
import time
import re
import csv
from io import StringIO
from dotenv import load_dotenv

from .models import (
    UserProfile, Skill, UserSkill, Achievement, UserAchievement,
    Challenge, UserChallenge, StudySession, Action, PersonalityTrait,
    UserPersonalityTrait, ActivityEvaluation, EvaluationTraitLink,
    ActivityArtifact, Resource, CheckedResource,
    StudySubject, StudyChapter, StudySection
)

from .serializers import (
    UserProfileSerializer, SkillSerializer, UserSkillSerializer,
    AchievementSerializer, UserAchievementSerializer,
    ChallengeSerializer, UserChallengeSerializer,
    StudySessionSerializer, ActionSerializer,
    DashboardStatsSerializer, LeaderboardSerializer,
    UserRankSerializer, ResourceSerializer,
    StudySubjectSerializer, StudyChapterSerializer, StudySectionSerializer
)

load_dotenv()

# ==================== HELPER FUNCTIONS ====================

def calculate_level_from_xp(total_xp):
    """✅ Calcule le level en fonction du total XP"""
    level = 1
    cumulative_xp = 0
    while True:
        xp_for_next = level * (level + 1) * 50
        if cumulative_xp + xp_for_next > total_xp:
            break
        cumulative_xp += xp_for_next
        level += 1
    return min(level, 1000)


# ==================== ERROR HANDLERS ====================

def handler404(request, exception=None):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


# ==================== AUTHENTICATION VIEWS ====================

@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if password != password_confirm:
            return render(request, 'register.html', {'error': 'Les mots de passe ne correspondent pas'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Cet utilisateur existe déjà'})

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user)
        login(request, user)
        return redirect('gamification:leaderboard')

    return render(request, 'register.html')


@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})


def index(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            return render(request, 'index.html', {'profile': profile})
        except UserProfile.DoesNotExist:
            return render(request, 'index.html', {'profile': None})
    return render(request, 'index.html')


# ==================== CLASS-BASED VIEWS ====================

@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                context['profile'] = UserProfile.objects.get(user=self.request.user)
            except UserProfile.DoesNotExist:
                context['profile'] = None
        return context


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'leaderboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            profile = UserProfile.objects.get(user=self.request.user)
            context['profile'] = profile
            context['active_challenges'] = UserChallenge.objects.filter(user=self.request.user, status='active').count()
            context['completed_challenges'] = UserChallenge.objects.filter(user=self.request.user,
                                                                           status='completed').count()
            context['recent_achievements'] = UserAchievement.objects.filter(user=self.request.user).order_by(
                '-unlocked_at')[:5]
            context['top_skills'] = UserSkill.objects.filter(user=self.request.user).order_by('-experience')[:3]
        except UserProfile.DoesNotExist:
            context['profile'] = None
        return context


@method_decorator(login_required, name='dispatch')
class ActionsView(TemplateView):
    template_name = 'actions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['actions'] = Action.objects.filter(user=self.request.user).order_by('-created_at')[:20]
        return context


@method_decorator(login_required, name='dispatch')
class AchievementsView(TemplateView):
    template_name = 'achievements.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['achievements'] = UserAchievement.objects.filter(user=self.request.user).order_by('-unlocked_at')
        return context


@method_decorator(login_required, name='dispatch')
class ChallengesView(TemplateView):
    template_name = 'challenges.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['challenges'] = UserChallenge.objects.filter(user=self.request.user).order_by('-challenge__start_date')
        return context


@method_decorator(login_required, name='dispatch')
class StudyTrackerView(TemplateView):
    template_name = 'study_tracker.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = StudySession.objects.filter(user=self.request.user).order_by('-started_at')[:20]
        return context


@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            profile = UserProfile.objects.get(user=self.request.user)
            context['profile'] = profile
            context['user'] = self.request.user
        except UserProfile.DoesNotExist:
            context['profile'] = None
        return context


@method_decorator(login_required, name='dispatch')
class SettingsView(TemplateView):
    template_name = 'settings.html'


@method_decorator(login_required, name='dispatch')
class LeaderboardView(TemplateView):
    template_name = 'leaderboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        leaderboard = UserProfile.objects.all().order_by('-experience_points')[:50]
        context['leaderboard'] = leaderboard
        try:
            user_profile = UserProfile.objects.get(user=self.request.user)
            total_users = UserProfile.objects.count()
            rank = UserProfile.objects.filter(experience_points__gt=user_profile.experience_points).count() + 1
            context['user_rank'] = rank
            context['total_users'] = total_users
        except UserProfile.DoesNotExist:
            pass
        return context


@method_decorator(login_required, name='dispatch')
class SkillsView(TemplateView):
    template_name = 'skills_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = UserSkill.objects.filter(user=self.request.user).order_by('-experience')
        context['all_skills'] = Skill.objects.all()
        return context


# ==================== FUNCTION-BASED VIEWS ====================

@login_required
def skills_page(request):
    skills = UserSkill.objects.filter(user=request.user)
    return render(request, 'skills_page.html', {'skills': skills})


# ==================== API ENDPOINTS - PROFILE ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """✅ Récupère le profil utilisateur"""
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        user = request.user

        profile_image_url = None
        cover_image_url = None

        if profile.profile_image:
            profile_image_url = request.build_absolute_uri(profile.profile_image.url)
        if profile.cover_image:
            cover_image_url = request.build_absolute_uri(profile.cover_image.url)

        data = {
            'id': profile.id,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'level': profile.level,
            'experience_points': profile.experience_points,
            'total_points': profile.total_points,
            'badges_count': profile.badges_count,
            'profile_image_url': profile_image_url,
            'cover_image_url': cover_image_url,
            'galaxy': profile.galaxy,
            'level_in_galaxy': profile.level_in_galaxy,
            'galaxy_name': profile.galaxy_name,
            'created_at': profile.created_at.isoformat() if profile.created_at else None,
            'updated_at': profile.updated_at.isoformat() if profile.updated_at else None
        }

        return Response(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """✅ Met à jour le profil utilisateur"""
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        user = request.user

        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()

        profile_image_url = None
        cover_image_url = None

        if profile.profile_image:
            profile_image_url = request.build_absolute_uri(profile.profile_image.url)
        if profile.cover_image:
            cover_image_url = request.build_absolute_uri(profile.cover_image.url)

        data = {
            'id': profile.id,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'level': profile.level,
            'experience_points': profile.experience_points,
            'total_points': profile.total_points,
            'badges_count': profile.badges_count,
            'profile_image_url': profile_image_url,
            'cover_image_url': cover_image_url,
            'galaxy': profile.galaxy,
            'level_in_galaxy': profile.level_in_galaxy,
            'galaxy_name': profile.galaxy_name
        }

        return Response(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== API ENDPOINTS - UPLOAD IMAGES ====================

@require_http_methods(['GET'])
@login_required
def api_get_profile_images(request):
    """
    ✅ NOUVELLE FONCTION - Récupère les URLs des images de profil et de couverture
    Cette fonction résout le problème de persistance des images
    """
    try:
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        avatar_url = None
        cover_url = None
        
        # Vérifier si l'image de profil existe
        if profile.profile_image and hasattr(profile.profile_image, 'url'):
            try:
                avatar_url = request.build_absolute_uri(profile.profile_image.url)
            except Exception as e:
                print(f"❌ Erreur lors de la récupération de l'avatar: {e}")
        
        # Vérifier si l'image de couverture existe
        if profile.cover_image and hasattr(profile.cover_image, 'url'):
            try:
                cover_url = request.build_absolute_uri(profile.cover_image.url)
            except Exception as e:
                print(f"❌ Erreur lors de la récupération de la couverture: {e}")
        
        print(f"✅ Images chargées - Avatar: {avatar_url}, Cover: {cover_url}")
        
        return JsonResponse({
            'success': True,
            'avatar_url': avatar_url,
            'cover_url': cover_url,
            'user': user.username
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(['POST'])
@login_required
def api_upload_profile_image(request):
    """✅ Upload l'image de profil (VERSION AMÉLIORÉE)"""
    try:
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)

        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'Aucune image fournie'}, status=400)

        image_file = request.FILES['image']

        # Validation du type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return JsonResponse({'success': False, 'error': 'Type non autorisé'}, status=400)

        # Validation de la taille (5MB max)
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'Image trop grande (max 5MB)'}, status=400)

        # Supprimer l'ancienne image si elle existe
        if profile.profile_image:
            try:
                profile.profile_image.delete(save=False)
            except Exception as e:
                print(f"⚠️ Impossible de supprimer l'ancienne image: {e}")

        # Sauvegarder la nouvelle image
        profile.profile_image = image_file
        profile.save()

        # Construire l'URL absolue
        image_url = request.build_absolute_uri(profile.profile_image.url)
        
        print(f"✅ Image de profil uploadée: {image_url}")

        return JsonResponse({
            'success': True,
            'message': 'Image de profil sauvegardée avec succès',
            'image_url': image_url,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(['POST'])
@login_required
def api_upload_cover_image(request):
    """✅ Upload l'image de couverture (VERSION AMÉLIORÉE)"""
    try:
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)

        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'Aucune image fournie'}, status=400)

        image_file = request.FILES['image']

        # Validation du type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return JsonResponse({'success': False, 'error': 'Type non autorisé'}, status=400)

        # Validation de la taille (10MB max)
        if image_file.size > 10 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'Image trop grande (max 10MB)'}, status=400)

        # Supprimer l'ancienne image si elle existe
        if profile.cover_image:
            try:
                profile.cover_image.delete(save=False)
            except Exception as e:
                print(f"⚠️ Impossible de supprimer l'ancienne image: {e}")

        # Sauvegarder la nouvelle image
        profile.cover_image = image_file
        profile.save()

        # Construire l'URL absolue
        image_url = request.build_absolute_uri(profile.cover_image.url)
        
        print(f"✅ Image de couverture uploadée: {image_url}")

        return JsonResponse({
            'success': True,
            'message': 'Image de couverture sauvegardée avec succès',
            'image_url': image_url,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ==================== API ENDPOINTS - GET USER DATA ====================

@login_required
@require_http_methods(["GET"])
def api_get_user_data(request):
    """
    ✅ Récupère les données utilisateur COMPLÈTES
    Retourne: XP, Level, Traits HP, Évaluations, IMAGES, DÉTECTIONS
    """
    try:
        user = request.user

        # 1. RÉCUPÉRER LE PROFIL
        try:
            profile = UserProfile.objects.get(user=user)
            total_xp = profile.experience_points
            level = profile.level
            profile_image_url = profile.profile_image.url if profile.profile_image else None
            cover_image_url = profile.cover_image.url if profile.cover_image else None
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
            total_xp = 0
            level = 1
            profile_image_url = None
            cover_image_url = None

        # 2. RÉCUPÉRER LES TRAITS ET LEURS HP
        traits_hp = {}
        user_traits = UserPersonalityTrait.objects.filter(user=user)
        for user_trait in user_traits:
            traits_hp[user_trait.trait.name] = user_trait.hp

        # 3. RÉCUPÉRER LES DÉTECTIONS CUMULÉES DEPUIS ActivityEvaluation
        detections = {
            'booksRead': 0,
            'academicArticles': 0,
            'projectsWorked': 0,
            'onlineCourses': 0,
            'socialContributions': 0,
            'networkingEvents': 0
        }

        # 4. RÉCUPÉRER LES ÉVALUATIONS
        evaluations_list = []
        activity_evals = ActivityEvaluation.objects.filter(user=user).order_by('-created_at')

        for eval_obj in activity_evals:
            # Cumule les détections
            detections['booksRead'] += eval_obj.books_read or 0
            detections['academicArticles'] += eval_obj.academic_articles or 0
            detections['projectsWorked'] += eval_obj.projects_worked or 0
            detections['onlineCourses'] += eval_obj.online_courses or 0
            detections['socialContributions'] += eval_obj.social_contributions or 0
            detections['networkingEvents'] += eval_obj.networking_events or 0

            # Traits de cette évaluation
            eval_traits = []
            trait_links = EvaluationTraitLink.objects.filter(evaluation=eval_obj)
            for link in trait_links:
                eval_traits.append({
                    'name': link.trait.name,
                    'category': link.trait.get_category_display(),
                    'hpAwarded': link.hp_awarded,
                    'relevance': link.relevance
                })

            evaluations_list.append({
                'id': eval_obj.id,
                'description': eval_obj.description,
                'isValid': eval_obj.is_valid,
                'xpAwarded': eval_obj.xp_awarded,
                'qualityScore': eval_obj.quality_score,
                'feedback': eval_obj.ai_feedback,
                'type': 'ia',
                'traits': eval_traits,
                'detections': {
                    'booksRead': eval_obj.books_read or 0,
                    'academicArticles': eval_obj.academic_articles or 0,
                    'projectsWorked': eval_obj.projects_worked or 0,
                    'onlineCourses': eval_obj.online_courses or 0,
                    'socialContributions': eval_obj.social_contributions or 0,
                    'networkingEvents': eval_obj.networking_events or 0
                },
                'createdAt': eval_obj.created_at.isoformat() if eval_obj.created_at else None
            })

        # ✅ AJOUTER LES IMAGES ET DÉTECTIONS À LA RÉPONSE
        response_data = {
            'success': True,
            'totalXP': total_xp,
            'level': level,
            'traitsHP': traits_hp,
            'evaluations': evaluations_list,
            'detections': detections,
            'acquired_skills': profile.acquired_skills or [],
            'discovered_categories': profile.discovered_categories or [],
            'explored_domains': profile.explored_domains or [],
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'firstName': user.first_name,
                'lastName': user.last_name,
                'profileImage': profile_image_url,
                'coverImage': cover_image_url
            }
        }

        return JsonResponse(response_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ==================== API ENDPOINTS - DAILY ACTIVITIES ====================

@require_http_methods(["POST"])
@require_http_methods(["POST"])
@login_required
def api_save_daily_activity(request):
    """✅ Sauvegarde les activités quotidiennes - VERSION AMÉLIORÉE avec support barèmes sommeil"""
    try:
        data = json.loads(request.body)
        activities = data.get('activities', [])
        if not activities:
            return JsonResponse({'success': False, 'error': 'Aucune activité fournie'}, status=400)

        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        # Map de scoring de base - utilisé si le frontend n'envoie pas de HP calculés
        FALLBACK_SCORING_MAP = {
            1: {'xp': 50, 'traits': {'Résilience': 30, 'Discipline': 50}},
            2: {'xp': 40, 'traits': {'Discipline': 40}},
            3: {'xp': 60, 'traits': {'Discipline': 35, 'Apprentissage': 50}},
            4: {'xp': 45, 'traits': {'Discipline': 45}},
            5: {'xp': 35, 'traits': {'Discipline': 35}},
            6: {'xp': 70, 'traits': {'Discipline': 50, 'Accomplissement': 40}},
            7: {'xp': 55, 'traits': {'Discipline': 45}},
            8: {'xp': 30, 'traits': {'Discipline': 30}},
            9: {'xp': 50, 'traits': {'Discipline': 40, 'Ambition': 30}},
            10: {'xp': 60, 'traits': {'Discipline': 50}},
            11: {'xp': 40, 'traits': {'Apprentissage': 40}},
            12: {'xp': 35, 'traits': {'Discipline': 35}},
            13: {'xp': 65, 'traits': {'Discipline': 50, 'Ambition': 40}},
            14: {'xp': 45, 'traits': {'Discipline': 40}},
            15: {'xp': 50, 'traits': {'Discipline': 50}},
            16: {'xp': 55, 'traits': {'Discipline': 45, 'Ambition': 35}},
            17: {'xp': 40, 'traits': {'Résilience': 35}},
            18: {'xp': 45, 'traits': {'Discipline': 45}},
            19: {'xp': 70, 'traits': {'Discipline': 60, 'Ambition': 50}},
            20: {'xp': 50, 'traits': {'Discipline': 50}},
            21: {'xp': 60, 'traits': {'Discipline': 50, 'Apprentissage': 40}},
            22: {'xp': 55, 'traits': {'Discipline': 45, 'Ambition': 35}},
            23: {'xp': 75, 'traits': {'Discipline': 60, 'Accomplissement': 50}},
        }

        total_xp = 0
        traits_hp_gained = {}
        eval_description = f"Activités quotidiennes: {len(activities)} activités"

        evaluation = ActivityEvaluation.objects.create(
            user=user,
            description=eval_description,
            is_valid=True,
            ai_feedback="Activités quotidiennes enregistrées"
        )

        for activity in activities:
            activity_id = activity.get('id')
            activity_name = activity.get('name', f'Activité {activity_id}')
            
            # ✅ NOUVEAU: Si le frontend envoie les HP calculés (pour sommeil/sieste avec barèmes)
            if 'hp' in activity and 'traits' in activity:
                hp_total = activity.get('hp', 0)
                traits_from_frontend = activity.get('traits', [])
                
                # Calculer la somme des HP de base des traits
                base_hp_sum = sum(t.get('hp', 0) for t in traits_from_frontend)
                
                # Appliquer le ratio aux traits
                for trait_info in traits_from_frontend:
                    trait_name = trait_info.get('name')
                    base_trait_hp = trait_info.get('hp', 0)
                    
                    if trait_name and base_hp_sum > 0:
                        # Calculer le HP proportionnel basé sur le HP total calculé
                        # Exemple: Si sommeil devrait donner 200 HP base mais donne 150 HP réel
                        # Et un trait vaut 120 HP base, il recevra (120/200) * 150 = 90 HP
                        hp_amount = int((base_trait_hp / base_hp_sum) * hp_total)
                        
                        traits_hp_gained[trait_name] = traits_hp_gained.get(trait_name, 0) + hp_amount
                        
                        trait, _ = PersonalityTrait.objects.get_or_create(
                            name=trait_name,
                            defaults={'category': 'behavioral'}
                        )

                        EvaluationTraitLink.objects.create(
                            evaluation=evaluation,
                            trait=trait,
                            hp_awarded=hp_amount,
                            relevance=f"{activity_name}: {trait_name}"
                        )

                        user_trait, created = UserPersonalityTrait.objects.get_or_create(
                            user=user,
                            trait=trait
                        )

                        user_trait.hp += hp_amount
                        user_trait.save()
                        
            # ✅ ANCIEN: Fallback pour les activités qui utilisent le scoring map
            elif activity_id in FALLBACK_SCORING_MAP:
                scoring = FALLBACK_SCORING_MAP[activity_id]
                total_xp += scoring['xp']

                for trait_name, hp_amount in scoring['traits'].items():
                    traits_hp_gained[trait_name] = traits_hp_gained.get(trait_name, 0) + hp_amount

                    trait, _ = PersonalityTrait.objects.get_or_create(
                        name=trait_name,
                        defaults={'category': 'behavioral'}
                    )

                    EvaluationTraitLink.objects.create(
                        evaluation=evaluation,
                        trait=trait,
                        hp_awarded=hp_amount,
                        relevance=f"{activity_name}: {trait_name}"
                    )

                    user_trait, created = UserPersonalityTrait.objects.get_or_create(
                        user=user,
                        trait=trait
                    )

                    user_trait.hp += hp_amount
                    user_trait.save()

        evaluation.xp_awarded = 0
        evaluation.save()

        profile.experience_points += total_xp
        profile.level = calculate_level_from_xp(profile.experience_points)
        profile.total_points += total_xp
        profile.save()

        Action.objects.create(
            user=user,
            action_type='quotidien',
            description=eval_description,
            points=0
        )

        return JsonResponse({
            'success': True,
            'message': 'Activités enregistrées',
            'total_xp': total_xp,
            'traits_hp': traits_hp_gained,
            'level': profile.level,
            'evaluation_id': evaluation.id
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



@require_http_methods(["GET"])
@login_required
def api_get_streak(request):
    """✅ Récupère la streak de l'utilisateur"""
    try:
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        today = timezone.now().date()
        streak = 0
        current_date = today

        while True:
            actions = Action.objects.filter(user=user, created_at__date=current_date)
            if actions.exists():
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break

        return JsonResponse({'success': True, 'streak': streak, 'last_activity': profile.experience_points})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ==================== API ENDPOINTS - DAY PLANNING ====================

@require_http_methods(["POST"])
@login_required
def api_validate_day_planning(request):
    """✅ Valide le planning de la journée"""
    try:
        data = json.loads(request.body)
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        hp_rewards = {
            'Discipline': 25,
            'Organisation': 20,
            'Exécution': 20,
            'Accomplissement': 15,
            'Ambition': 10
        }

        evaluation = ActivityEvaluation.objects.create(
            user=user,
            description="Planning validé",
            is_valid=True,
            xp_awarded=0,
            ai_feedback="Planning de la journée validé"
        )

        traits_hp_gained = {}

        for trait_name, hp_amount in hp_rewards.items():
            traits_hp_gained[trait_name] = hp_amount

            trait, _ = PersonalityTrait.objects.get_or_create(
                name=trait_name,
                defaults={'category': 'behavioral'}
            )

            EvaluationTraitLink.objects.create(
                evaluation=evaluation,
                trait=trait,
                hp_awarded=hp_amount,
                relevance=f"Planning validé: {trait_name}"
            )

            user_trait, created = UserPersonalityTrait.objects.get_or_create(
                user=user,
                trait=trait
            )

            user_trait.hp += hp_amount
            user_trait.save()

        Action.objects.create(
            user=user,
            action_type='day_validated',
            description="Planning validé",
            points=0
        )

        return JsonResponse({
            'success': True,
            'hp_gained': 90,
            'traits_hp': traits_hp_gained,
            'evaluation_id': evaluation.id
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ==================== API ENDPOINTS - IA EVALUATION ====================

@require_http_methods(["POST"])
@login_required
def api_evaluate_activity(request):
    """✅ Évalue une activité avec l'IA - VERSION CORRIGÉE
    
    Cette fonction ANALYSE SEULEMENT l'activité et retourne les résultats.
    Elle NE DOIT PAS enregistrer en base de données.
    L'enregistrement se fait uniquement via api_confirm_evaluation().
    """
    try:
        data = json.loads(request.body)
        description = data.get('description', '')
        user = request.user

        if not description:
            return JsonResponse({'success': False, 'error': 'Description vide'}, status=400)

        profile, _ = UserProfile.objects.get_or_create(user=user)

        api_key = os.getenv('PERPLEXITY_API_KEY')
        if not api_key:
            return JsonResponse({'success': False, 'error': 'PERPLEXITY_API_KEY not configured'}, status=400)

        # 🔍 DEBUG
        print("\n" + "=" * 100)
        print("📊 ANALYSE IA (SANS ENREGISTREMENT)")
        print(f"   User: {user.username}")
        print(f"   Description: {description[:100]}...")
        print("=" * 100)

        prompt = f"""Analyse cette activité et retourne UNIQUEMENT du JSON (pas de texte avant/après):

Activité: {description}

Retourne ce JSON valide:
{{
"isValid": true,
"xpAmount": 100,
"qualityScore": 0.8,
"feedback": "Analyse courte",
"personalityTraits": [
{{"name": "Discipline", "hpAmount": 35, "relevance": "Effort soutenu"}}
],
"detections": {{
"booksRead": 0,
"academicArticles": 0,
"projectsWorked": 0,
"onlineCourses": 0,
"socialContributions": 0,
"networkingEvents": 0
}}
}}"""

        headers = {'Authorization': f'Bearer {api_key}'}
        payload = {
            'model': 'sonar',
            'messages': [{'role': 'user', 'content': prompt}]
        }

        print("📤 Appel API Perplexity...")
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Erreur API: {response.status_code}")
            return JsonResponse({'success': False, 'error': f'API error: {response.status_code}'}, status=400)

        result = response.json()
        content = result['choices'][0]['message']['content']
        
        print("📥 Réponse IA reçue")

        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            print("❌ Impossible de parser la réponse")
            return JsonResponse({'success': False, 'error': 'Could not parse AI response'}, status=400)

        evaluation_data = json.loads(json_match.group())
        
        # 📊 Calculer les totaux pour affichage
        total_xp = evaluation_data.get('xpAmount', 50) if evaluation_data.get('isValid') else 0
        
        # Convertir les traits au format attendu par le frontend
        traits_for_frontend = []
        traits_hp_dict = {}
        
        for trait_data in evaluation_data.get('personalityTraits', []):
            trait_name = trait_data.get('name')
            hp_amount = trait_data.get('hpAmount', 0)
            relevance = trait_data.get('relevance', '')
            
            traits_for_frontend.append({
                'name': trait_name,
                'hp_amount': hp_amount,  # Note: hp_amount (pas hpAmount) pour le frontend
                'relevance': relevance
            })
            
            traits_hp_dict[trait_name] = hp_amount
        
        print(f"\n✅ ANALYSE TERMINÉE (AUCUN ENREGISTREMENT)")
        print(f"   XP calculé: {total_xp}")
        print(f"   Traits détectés: {len(traits_for_frontend)}")
        for trait in traits_for_frontend:
            print(f"      - {trait['name']}: {trait['hp_amount']} HP")
        print(f"   Artéfacts: {evaluation_data.get('detections', {})}")
        print("=" * 100 + "\n")

        # ✅ RETOURNE SEULEMENT LES DONNÉES (PAS D'ENREGISTREMENT!)
        return JsonResponse({
            'success': True,
            'total_xp': total_xp,
            'traits_hp': traits_hp_dict,  # Pour l'affichage du total HP
            'personality_traits': traits_for_frontend,  # Pour l'enregistrement ultérieur
            'detections': evaluation_data.get('detections', {}),
            'quality_score': evaluation_data.get('qualityScore', 0.5),
            'feedback': evaluation_data.get('feedback', ''),
            'is_valid': evaluation_data.get('isValid', True),
            'level': profile.level,
            # ⚠️ PAS d'evaluation_id car rien n'a été créé en base!
        })
        
    except Exception as e:
        print("\n❌ ERREUR DANS api_evaluate_activity:")
        print(f"❌ {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_http_methods(["POST"])
@login_required
def api_confirm_evaluation(request):
    """✅ Confirme une évaluation IA - VERSION CORRIGÉE
    
    Cette fonction est la SEULE qui enregistre les données en base.
    Elle reçoit les données de api_evaluate_activity et les enregistre.
    """
    try:
        data = json.loads(request.body)
        user = request.user
        description = data.get('description', '')
        xp_amount = data.get('xp_amount', 0)
        quality_score = data.get('quality_score', 0)
        feedback = data.get('feedback', '')
        personality_traits = data.get('personality_traits', [])
        detections = data.get('detections', {})
        
        # 🔍 DEBUG: Afficher les données reçues
        print("\n" + "=" * 100)
        print("📊 CONFIRMATION D'ÉVALUATION IA (ENREGISTREMENT EN BASE)")
        print(f"   User: {user.username}")
        print(f"   Description: {description[:100]}...")
        print(f"   XP Amount: {xp_amount}")
        print(f"   Quality Score: {quality_score}")
        print(f"   Nombre de traits: {len(personality_traits)}")
        print(f"   Traits reçus:")
        for i, trait_data in enumerate(personality_traits):
            print(f"      {i+1}. {trait_data.get('name')} → {trait_data.get('hp_amount')} HP")
        print(f"   Artéfacts détectés: {detections}")
        print("=" * 100)
        
        # ✅ CRÉER L'ÉVALUATION EN BASE
        evaluation = ActivityEvaluation.objects.create(
            user=user,
            description=description,
            xp_awarded=xp_amount,
            quality_score=quality_score,
            ai_feedback=feedback,
            is_valid=True,
            # Enregistrer les artéfacts
            books_read=detections.get('booksRead', 0),
            academic_articles=detections.get('academicArticles', 0),
            projects_worked=detections.get('projectsWorked', 0),
            online_courses=detections.get('onlineCourses', 0),
            social_contributions=detections.get('socialContributions', 0),
            networking_events=detections.get('networkingEvents', 0),
        )
        print(f"✅ Évaluation créée (ID: {evaluation.id})")
        
        # ✅ METTRE À JOUR LE PROFIL UTILISATEUR (XP)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        old_xp = profile.experience_points
        profile.experience_points += xp_amount
        profile.level = calculate_level_from_xp(profile.experience_points)
        profile.save()
        print(f"✅ Profil mis à jour: XP {old_xp} → {profile.experience_points} (Niveau {profile.level})")
        
        # Compteurs
        traits_processed = 0
        traits_errors = []
        total_hp_awarded = 0
        
        # ✅ TRAITER LES TRAITS
        for trait_index, trait_data in enumerate(personality_traits):
            try:
                trait_name = trait_data.get('name')
                hp_amount = trait_data.get('hp_amount', 0)
                relevance = trait_data.get('relevance', 'Détecté par IA')
                
                print(f"\n🔹 Trait #{trait_index+1}: {trait_name}")
                print(f"   HP: {hp_amount} (type: {type(hp_amount)})")
                
                # Vérifier que hp_amount est bien un nombre
                if not isinstance(hp_amount, (int, float)):
                    error_msg = f"hp_amount invalide pour {trait_name}: {hp_amount} (type: {type(hp_amount)})"
                    print(f"   ⚠️  {error_msg}")
                    traits_errors.append(error_msg)
                    hp_amount = 0
                
                if not trait_name:
                    error_msg = f"Nom de trait manquant à l'index {trait_index}"
                    print(f"   ❌ {error_msg}")
                    traits_errors.append(error_msg)
                    continue
                
                # Créer ou récupérer le trait
                trait, trait_created = PersonalityTrait.objects.get_or_create(
                    name=trait_name,
                    defaults={'category': 'behavioral'}
                )
                print(f"   {'🆕' if trait_created else '✓'} Trait {'créé' if trait_created else 'existant'}")
                
                # Créer le lien évaluation-trait
                eval_link = EvaluationTraitLink.objects.create(
                    evaluation=evaluation,
                    trait=trait,
                    hp_awarded=hp_amount,
                    relevance=relevance
                )
                print(f"   ✓ Lien créé (ID: {eval_link.id})")
                
                # Mettre à jour le trait utilisateur
                user_trait, ut_created = UserPersonalityTrait.objects.get_or_create(
                    user=user,
                    trait=trait
                )
                old_hp = user_trait.hp
                user_trait.hp += hp_amount
                user_trait.save()
                print(f"   ✓ UserTrait mis à jour: {old_hp} → {user_trait.hp} (+{hp_amount})")
                
                total_hp_awarded += hp_amount
                traits_processed += 1
                print(f"   ✅ Trait traité avec succès (Total: {traits_processed}/{len(personality_traits)})")
                
            except Exception as trait_error:
                error_msg = f"Erreur trait {trait_name}: {str(trait_error)}"
                traits_errors.append(error_msg)
                print(f"   ❌ {error_msg}")
                import traceback
                traceback.print_exc()
                # Continue avec les autres traits
                continue
        
        # ✅ CRÉER UNE ACTION
        Action.objects.create(
            user=user,
            action_type='evaluation_confirmed',
            description=f"Évaluation IA confirmée: {description[:50]}...",
            points=xp_amount
        )
        print(f"✅ Action créée")
        
        # Résumé
        print("\n" + "=" * 100)
        print("📊 RÉSUMÉ DE L'ENREGISTREMENT:")
        print(f"   ✅ Traits traités: {traits_processed}/{len(personality_traits)}")
        print(f"   ✅ HP total attribué: {total_hp_awarded}")
        print(f"   ✅ XP attribué: {xp_amount}")
        print(f"   ✅ Niveau: {profile.level}")
        print(f"   ✅ Artéfacts enregistrés:")
        print(f"      - Livres: {detections.get('booksRead', 0)}")
        print(f"      - Articles: {detections.get('academicArticles', 0)}")
        print(f"      - Projets: {detections.get('projectsWorked', 0)}")
        print(f"      - Cours: {detections.get('onlineCourses', 0)}")
        print(f"      - Contributions: {detections.get('socialContributions', 0)}")
        print(f"      - Networking: {detections.get('networkingEvents', 0)}")
        
        if traits_errors:
            print(f"\n   ⚠️  Erreurs rencontrées ({len(traits_errors)}):")
            for error in traits_errors:
                print(f"      - {error}")
        
        print("=" * 100 + "\n")
        
        # Retourner la réponse
        response_data = {
            'success': True,
            'evaluation_id': evaluation.id,
            'traits_processed': traits_processed,
            'total_traits': len(personality_traits),
            'total_hp_awarded': total_hp_awarded,
            'xp_awarded': xp_amount,
            'new_level': profile.level,
            'artifacts_saved': {
                'booksRead': detections.get('booksRead', 0),
                'academicArticles': detections.get('academicArticles', 0),
                'projectsWorked': detections.get('projectsWorked', 0),
                'onlineCourses': detections.get('onlineCourses', 0),
                'socialContributions': detections.get('socialContributions', 0),
                'networkingEvents': detections.get('networkingEvents', 0),
            }
        }
        
        if traits_errors:
            response_data['warnings'] = traits_errors
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print("\n" + "=" * 100)
        print("❌ ERREUR GLOBALE dans api_confirm_evaluation:")
        print(f"❌ {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 100 + "\n")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
        
# ==================== API ENDPOINTS - LEGACY/COMPATIBILITY ====================

@require_http_methods(["POST"])
@login_required
def api_save_challenge_data(request):
    """✅ Sauvegarde les données de défi"""
    try:
        data = json.loads(request.body)
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        evaluation = ActivityEvaluation.objects.create(
            user=user,
            description=data.get('description', 'Défi complété'),
            is_valid=True,
            xp_awarded=data.get('xp_amount', 50),
            ai_feedback="Défi validé"
        )

        profile.experience_points += data.get('xp_amount', 50)
        profile.level = calculate_level_from_xp(profile.experience_points)
        profile.total_points += data.get('xp_amount', 50)
        profile.save()

        Action.objects.create(
            user=user,
            action_type='challenge',
            description=data.get('description', 'Défi complété'),
            points=data.get('xp_amount', 50)
        )

        return JsonResponse({
            'success': True,
            'total_xp': data.get('xp_amount', 50),
            'level': profile.level,
            'evaluation_id': evaluation.id
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
@login_required
def api_add_time_block(request):
    """✅ Ajoute un bloc de temps"""
    try:
        data = json.loads(request.body)
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        evaluation = ActivityEvaluation.objects.create(
            user=user,
            description=f"Bloc de temps: {data.get('title', 'Sans titre')}",
            is_valid=True,
            xp_awarded=data.get('xp_amount', 30),
            ai_feedback="Bloc de temps enregistré"
        )

        profile.experience_points += data.get('xp_amount', 30)
        profile.level = calculate_level_from_xp(profile.experience_points)
        profile.total_points += data.get('xp_amount', 30)
        profile.save()

        Action.objects.create(
            user=user,
            action_type='time_block',
            description=f"Bloc: {data.get('title', 'Sans titre')}",
            points=data.get('xp_amount', 30)
        )

        return JsonResponse({
            'success': True,
            'total_xp': data.get('xp_amount', 30),
            'level': profile.level,
            'evaluation_id': evaluation.id
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
@login_required
def api_toggle_time_block(request):
    """✅ Bascule l'état d'un bloc de temps"""
    try:
        data = json.loads(request.body)
        user = request.user
        status = data.get('status', 'completed')

        Action.objects.create(
            user=user,
            action_type='time_block_toggled',
            description=f"Bloc de temps: {status}",
            points=0
        )

        return JsonResponse({'success': True, 'status': status})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
@login_required
def api_validate_day(request):
    """✅ Valide la journée"""
    try:
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        profile.experience_points += 100
        profile.level = calculate_level_from_xp(profile.experience_points)
        profile.total_points += 100
        profile.save()

        Action.objects.create(
            user=user,
            action_type='day_validated',
            description="Journée validée",
            points=100
        )

        return JsonResponse({'success': True, 'total_xp': 100, 'level': profile.level})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ==================== API ENDPOINTS - SKILLS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_skill(request):
    """
    ✅ Ajoute une compétence à l'utilisateur
    Source de vérité : UserProfile.acquired_skills (JSON)
    """
    try:
        skill_name = request.data.get('skill')

        if not skill_name or not isinstance(skill_name, str):
            return Response(
                {'success': False, 'error': 'Champ "skill" invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        # Initialisation défensive
        if profile.acquired_skills is None:
            profile.acquired_skills = []

        # Normalisation (évite doublons invisibles)
        skill_name = skill_name.strip()

        if skill_name in profile.acquired_skills:
            return Response({
                'success': True,
                'message': 'Compétence déjà acquise',
                'acquired_skills': profile.acquired_skills
            }, status=status.HTTP_200_OK)

        # Ajout réel
        profile.acquired_skills.append(skill_name)
        profile.save(update_fields=['acquired_skills'])

        return Response({
            'success': True,
            'message': f'✅ Compétence "{skill_name}" ajoutée',
            'acquired_skills': profile.acquired_skills,
            'total_skills': len(profile.acquired_skills)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_category(request):
    """Ajouter une catégorie"""
    try:
        category_name = request.data.get('category_name')
        if not category_name:
            return Response({'error': 'category_name requis'}, status=400)

        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        if not profile.discovered_categories:
            profile.discovered_categories = []

        if category_name not in profile.discovered_categories:
            profile.discovered_categories.append(category_name)
            profile.save()

        return Response({
            'success': True,
            'message': f'✅ Catégorie "{category_name}" ajoutée',
            'discovered_categories': profile.discovered_categories
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_domain(request):
    """Ajouter un domaine"""
    try:
        domain_name = request.data.get('domain_name')
        if not domain_name:
            return Response({'error': 'domain_name requis'}, status=400)

        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        if not profile.explored_domains:
            profile.explored_domains = []

        if domain_name not in profile.explored_domains:
            profile.explored_domains.append(domain_name)
            profile.save()

        return Response({
            'success': True,
            'message': f'✅ Domaine "{domain_name}" ajouté',
            'explored_domains': profile.explored_domains
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_skills(request):
    """
    ✅ Retourne les compétences depuis UserProfile
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    return Response({
        'success': True,
        'acquired_skills': profile.acquired_skills or [],
        'total_skills': len(profile.acquired_skills or [])
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_skill_details(request, skill_id):
    """Récupère les détails d'une compétence spécifique"""
    try:
        skill = Skill.objects.get(id=skill_id)
        serializer = SkillSerializer(skill)
        return Response(serializer.data)
    except Skill.DoesNotExist:
        return Response({'error': 'Skill not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_domain_progress(request, domain):
    """Récupère la progression par domaine"""
    skills = UserSkill.objects.filter(user=request.user, skill__name__icontains=domain)
    total_skills = skills.count()
    completed_skills = skills.filter(mastery_percentage=100).count()
    average_mastery = skills.aggregate(Avg('mastery_percentage'))['mastery_percentage__avg'] or 0

    data = {
        'domain': domain,
        'total_skills': total_skills,
        'completed_skills': completed_skills,
        'average_mastery': average_mastery,
        'overall_progress': (completed_skills / total_skills * 100) if total_skills > 0 else 0
    }

    return Response(data)


# ==================== API ENDPOINTS - LEADERBOARD ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_leaderboard(request):
    """✅ Récupère le classement global AVEC les photos ET les HP (OPTIMISÉ)"""
    try:
        # ✅ OPTIMISATION : Utiliser select_related et prefetch_related pour éviter N+1
        leaderboard = UserProfile.objects.select_related('user').all().order_by('-experience_points')[:50]
        
        data = []

        for idx, profile in enumerate(leaderboard, 1):
            profile_image_url = None
            if profile.profile_image:
                try:
                    profile_image_url = request.build_absolute_uri(profile.profile_image.url)
                except Exception as e:
                    print(f'⚠️ Erreur image pour {profile.user.username}: {e}')
                    profile_image_url = None

            # ✅ CALCULER LES HP DEPUIS LES TRAITS (déjà chargés en mémoire)
            total_hp = 0
            try:
                traits = UserPersonalityTrait.objects.filter(user=profile.user)
                for trait in traits:
                    # Vérifier que l'attribut hp existe et n'est pas None
                    if hasattr(trait, 'hp') and trait.hp is not None:
                        total_hp += int(trait.hp)
            except Exception as e:
                print(f'⚠️ Erreur HP pour {profile.user.username}: {e}')
                total_hp = 0

            data.append({
                'rank': idx,
                'username': profile.user.username,
                'user_id': profile.user.id,
                'level': profile.level,
                'experience_points': profile.experience_points,
                'total_points': profile.total_points,
                'total_hp': total_hp,  # ✅ HP totaux
                'badges_count': profile.badges_count,
                'profile_image_url': profile_image_url
            })

        print(f'✅ Leaderboard chargé: {len(data)} joueurs avec HP')
        return Response(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f'❌ ERREUR LEADERBOARD: {str(e)}')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_leaderboard_weekly(request):
    """✅ Récupère le classement hebdomadaire AVEC HP"""
    try:
        one_week_ago = timezone.now() - timedelta(days=7)
        weekly_data = []

        profiles = UserProfile.objects.select_related('user').all()

        for profile in profiles:
            weekly_points = Action.objects.filter(
                user=profile.user,
                created_at__gte=one_week_ago
            ).aggregate(Sum('points'))['points__sum'] or 0

            profile_image_url = None
            if profile.profile_image:
                try:
                    profile_image_url = request.build_absolute_uri(profile.profile_image.url)
                except Exception:
                    profile_image_url = None

            # ✅ CALCULER LES HP DEPUIS LES TRAITS
            total_hp = 0
            try:
                traits = UserPersonalityTrait.objects.filter(user=profile.user)
                for trait in traits:
                    if hasattr(trait, 'hp') and trait.hp is not None:
                        total_hp += int(trait.hp)
            except Exception:
                total_hp = 0

            weekly_data.append({
                'user_id': profile.user.id,
                'username': profile.user.username,
                'weekly_points': weekly_points,
                'total_hp': total_hp,
                'profile_image_url': profile_image_url
            })

        weekly_data.sort(key=lambda x: x['weekly_points'], reverse=True)
        result = [{'rank': idx, **u} for idx, u in enumerate(weekly_data[:50], 1)]

        return Response(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f'❌ ERREUR LEADERBOARD WEEKLY: {str(e)}')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_leaderboard_monthly(request):
    """✅ Récupère le classement mensuel AVEC HP"""
    try:
        one_month_ago = timezone.now() - timedelta(days=30)
        monthly_data = []

        profiles = UserProfile.objects.select_related('user').all()

        for profile in profiles:
            monthly_points = Action.objects.filter(
                user=profile.user,
                created_at__gte=one_month_ago
            ).aggregate(Sum('points'))['points__sum'] or 0

            profile_image_url = None
            if profile.profile_image:
                try:
                    profile_image_url = request.build_absolute_uri(profile.profile_image.url)
                except Exception:
                    profile_image_url = None

            # ✅ CALCULER LES HP DEPUIS LES TRAITS
            total_hp = 0
            try:
                traits = UserPersonalityTrait.objects.filter(user=profile.user)
                for trait in traits:
                    if hasattr(trait, 'hp') and trait.hp is not None:
                        total_hp += int(trait.hp)
            except Exception:
                total_hp = 0

            monthly_data.append({
                'user_id': profile.user.id,
                'username': profile.user.username,
                'monthly_points': monthly_points,
                'total_hp': total_hp,
                'profile_image_url': profile_image_url
            })

        monthly_data.sort(key=lambda x: x['monthly_points'], reverse=True)
        result = [{'rank': idx, **u} for idx, u in enumerate(monthly_data[:50], 1)]

        return Response(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f'❌ ERREUR LEADERBOARD MONTHLY: {str(e)}')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_leaderboard_simple(request):
    """Récupère le top 10 du classement AVEC HP"""
    leaderboard = UserProfile.objects.all().order_by('-experience_points')[:10]
    data = []
    
    for p in leaderboard:
        # Calculer les HP
        total_hp = sum([trait.hp for trait in UserPersonalityTrait.objects.filter(user=p.user)])
        data.append({
            'username': p.user.username,
            'level': p.level,
            'points': p.experience_points,
            'total_hp': total_hp
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_rank(request):
    """Récupère le rang de l'utilisateur"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        total_users = UserProfile.objects.count()
        rank = UserProfile.objects.filter(experience_points__gt=profile.experience_points).count() + 1
        percentile = ((total_users - rank) / total_users * 100) if total_users > 0 else 0

        data = {
            'rank': rank,
            'total_users': total_users,
            'percentile': percentile,
            'experience_points': profile.experience_points
        }

        return Response(data)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== API ENDPOINTS - ACHIEVEMENTS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_achievements(request):
    """Récupère les accomplissements de l'utilisateur"""
    achievements = UserAchievement.objects.filter(user=request.user)
    serializer = UserAchievementSerializer(achievements, many=True)
    return Response(serializer.data)


# ==================== API ENDPOINTS - CHALLENGES ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_challenges(request):
    """Récupère les défis actifs"""
    challenges = Challenge.objects.filter(is_active=True)
    serializer = ChallengeSerializer(challenges, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_challenge(request, challenge_id):
    """Complète un défi"""
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        user_challenge, created = UserChallenge.objects.get_or_create(user=request.user, challenge=challenge)
        user_challenge.status = 'completed'
        user_challenge.completed_at = timezone.now()
        user_challenge.save()

        serializer = UserChallengeSerializer(user_challenge)
        return Response(serializer.data)
    except Challenge.DoesNotExist:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== API ENDPOINTS - STUDY SESSIONS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_study_sessions(request):
    """Récupère les sessions d'étude"""
    sessions = StudySession.objects.filter(user=request.user).order_by('-started_at')
    serializer = StudySessionSerializer(sessions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_study_session(request):
    """Crée une session d'étude"""
    serializer = StudySessionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== API ENDPOINTS - DASHBOARD ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """Récupère les stats du dashboard"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        active_challenges = UserChallenge.objects.filter(user=request.user, status='active')
        completed_challenges = UserChallenge.objects.filter(user=request.user, status='completed')
        study_sessions = StudySession.objects.filter(user=request.user)
        total_study_time = study_sessions.aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
        recent_achievements = UserAchievement.objects.filter(user=request.user)[:5]
        top_skills = UserSkill.objects.filter(user=request.user).order_by('-experience')[:3]

        data = {
            'level': profile.level,
            'experience_points': profile.experience_points,
            'total_points': profile.total_points,
            'badges_count': profile.badges_count,
            'active_challenges_count': active_challenges.count(),
            'completed_challenges_count': completed_challenges.count(),
            'study_sessions_count': study_sessions.count(),
            'total_study_time_minutes': total_study_time,
            'recent_achievements': [a.achievement.name for a in recent_achievements],
            'top_skills': [s.skill.name for s in top_skills]
        }

        return Response(data)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== API ENDPOINTS - RESOURCES ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # ✅ CORRIGÉ : Authentification obligatoire
def api_get_all_resources(request):
    """✅ CORRIGÉ : Récupère TOUTES les ressources actives avec le niveau utilisateur
    et les ressources cochées."""
    try:
        # ✅ Récupérer le profil utilisateur
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_level = profile.level
        
        # ✅ Récupérer toutes les ressources actives
        resources = Resource.objects.filter(is_active=True).order_by('niveau')
        
        # ✅ Récupérer les ressources cochées par l'utilisateur
        checked_resources = CheckedResource.objects.filter(user=request.user).values_list('resource_id', flat=True)
        checked_list = list(checked_resources)

        # ✅ Formatter les ressources
        data = [
            {
                'id': r.id,
                'titre': r.titre,
                'auteur': r.auteur,
                'type': r.type,
                'domaine': r.domaine,
                'description': r.description,
                'niveau': r.niveau,
                'url': r.url,
                'image': r.image,
                'is_unlocked': r.niveau <= user_level  # ✅ Info si débloqué
            }
            for r in resources
        ]

        return Response({
            'success': True,
            'resources': data,
            'user_level': user_level,  # ✅ CORRIGÉ : Niveau utilisateur inclus
            'checked_resources': checked_list,  # ✅ CORRIGÉ : Ressources cochées
            'total_resources': len(data)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_resources_by_type(request, resource_type):
    """Récupère les ressources d'un type spécifique"""
    try:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_level = profile.level

        resources = Resource.objects.filter(
            is_active=True,
            type=resource_type,
            niveau__lte=user_level
        ).order_by('niveau')

        data = []

        for resource in resources:
            data.append({
                'id': resource.id,
                'titre': resource.titre,
                'auteur': resource.auteur,
                'type': resource.get_type_display(),
                'domaine': resource.domaine,
                'description': resource.description,
                'niveau': resource.niveau,
                'url': resource.url,
                'image': resource.image,
            })

        return Response({'success': True, 'resources': data, 'type': resource_type, 'count': len(data)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_search_resources(request):
    """Cherche les ressources"""
    try:
        query = request.GET.get('q', '').strip()
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_level = profile.level

        if not query:
            return Response({'success': False, 'error': 'Query vide'}, status=400)

        resources = Resource.objects.filter(is_active=True, niveau__lte=user_level).filter(
            Q(titre__icontains=query) | Q(auteur__icontains=query) | Q(description__icontains=query) | Q(
                domaine__icontains=query)
        ).order_by('niveau')

        data = []

        for resource in resources:
            data.append({
                'id': resource.id,
                'titre': resource.titre,
                'auteur': resource.auteur,
                'type': resource.get_type_display(),
                'domaine': resource.domaine,
                'description': resource.description,
                'niveau': resource.niveau,
                'url': resource.url,
            })

        return Response({'success': True, 'resources': data, 'query': query, 'count': len(data)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=400)


# ==================== API ENDPOINTS - REMOVE SKILL ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_skill(request):
    """✅ Supprime une compétence de l'utilisateur"""
    try:
        skill_name = request.data.get('skill')

        if not skill_name:
            return Response(
                {'success': False, 'error': 'skill_name requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Récupérer ou créer le profil utilisateur
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        # Initialiser si vide
        if not profile.acquired_skills:
            profile.acquired_skills = []

        # Convertir la liste en list si c'est une autre structure
        skills_list = list(profile.acquired_skills) if profile.acquired_skills else []

        # Chercher et supprimer la compétence
        if skill_name in skills_list:
            skills_list.remove(skill_name)
            profile.acquired_skills = skills_list
            profile.save()

            return Response({
                'success': True,
                'message': f'✅ Compétence "{skill_name}" supprimée',
                'acquired_skills': profile.acquired_skills,
                'total_skills': len(profile.acquired_skills)
            })
        else:
            return Response({
                'success': False,
                'error': f'Compétence "{skill_name}" non trouvée'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_category(request):
    """✅ Supprime une catégorie découverte"""
    try:
        category_name = request.data.get('category_name')

        if not category_name:
            return Response(
                {'success': False, 'error': 'category_name requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        if not profile.discovered_categories:
            profile.discovered_categories = []

        categories_list = list(profile.discovered_categories) if profile.discovered_categories else []

        if category_name in categories_list:
            categories_list.remove(category_name)
            profile.discovered_categories = categories_list
            profile.save()

            return Response({
                'success': True,
                'message': f'✅ Catégorie "{category_name}" supprimée',
                'discovered_categories': profile.discovered_categories
            })
        else:
            return Response({
                'success': False,
                'error': f'Catégorie "{category_name}" non trouvée'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_domain(request):
    """✅ Supprime un domaine exploré"""
    try:
        domain_name = request.data.get('domain_name')

        if not domain_name:
            return Response(
                {'success': False, 'error': 'domain_name requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        if not profile.explored_domains:
            profile.explored_domains = []

        domains_list = list(profile.explored_domains) if profile.explored_domains else []

        if domain_name in domains_list:
            domains_list.remove(domain_name)
            profile.explored_domains = domains_list
            profile.save()

            return Response({
                'success': True,
                'message': f'✅ Domaine "{domain_name}" supprimé',
                'explored_domains': profile.explored_domains
            })
        else:
            return Response({
                'success': False,
                'error': f'Domaine "{domain_name}" non trouvé'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ---- SUBJECTS ----

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_study_subjects(request):
    subjects = StudySubject.objects.filter(user=request.user)
    serializer = StudySubjectSerializer(subjects, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_study_subject(request):
    serializer = StudySubjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_study_subject(request, subject_id):
    try:
        subject = StudySubject.objects.get(id=subject_id, user=request.user)
    except StudySubject.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    # CASCADE supprime automatiquement les chapitres et sections liés
    subject.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ---- CHAPTERS ----

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_study_chapters(request):
    chapters = StudyChapter.objects.filter(user=request.user)
    serializer = StudyChapterSerializer(chapters, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_study_chapter(request):
    # Vérifie que la matière appartient à l'utilisateur
    subject_id = request.data.get('subject')
    if not StudySubject.objects.filter(id=subject_id, user=request.user).exists():
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = StudyChapterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_study_chapter(request, chapter_id):
    try:
        chapter = StudyChapter.objects.get(id=chapter_id, user=request.user)
    except StudyChapter.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    # CASCADE supprime automatiquement les sections liées
    chapter.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ---- SECTIONS ----

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_study_sections(request):
    sections = StudySection.objects.filter(user=request.user)
    serializer = StudySectionSerializer(sections, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_study_section(request):
    # Vérifie que la matière et le chapitre appartiennent à l'utilisateur
    subject_id = request.data.get('subject')
    chapter_id = request.data.get('chapter')
    if not StudySubject.objects.filter(id=subject_id, user=request.user).exists():
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)
    if not StudyChapter.objects.filter(id=chapter_id, user=request.user).exists():
        return Response({'error': 'Chapter not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = StudySectionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_study_section(request, section_id):
    try:
        section = StudySection.objects.get(id=section_id, user=request.user)
    except StudySection.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = StudySectionSerializer(section, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_study_section(request, section_id):
    try:
        section = StudySection.objects.get(id=section_id, user=request.user)
    except StudySection.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    section.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_resources(request):
    """Récupère toutes les ressources accessibles avec les cases cochées"""
    try:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_level = profile.level
        
        # Récupérer toutes les ressources actives
        all_resources = Resource.objects.filter(is_active=True).order_by('niveau')
        
        # Récupérer les ressources cochées par l'utilisateur
        checked_resources = CheckedResource.objects.filter(user=request.user).values_list('resource_id', flat=True)
        checked_list = list(checked_resources)
        
        # Formatter les ressources
        resources_list = []
        for resource in all_resources:
            resources_list.append({
                'id': resource.id,
                'titre': resource.titre,
                'auteur': resource.auteur,
                'type': resource.type,
                'domaine': resource.domaine,
                'description': resource.description,
                'niveau': resource.niveau,
                'url': resource.url,
                'image': resource.image,
            })
        
        return Response({
            'success': True,
            'resources': resources_list,
            'user': {
                'name': request.user.get_full_name() or request.user.username,
                'level': user_level,
                'checked_resources': checked_list  
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_toggle_resource(request):
    """Toggle une ressource cochée/décochée"""
    try:
        resource_id = request.data.get('resourceId')
        checked = request.data.get('checked')
        
        if not resource_id:
            return Response({
                'success': False, 
                'error': 'resourceId manquant'
            }, status=400)
        
        if checked:
            # Ajouter la ressource cochée
            CheckedResource.objects.get_or_create(
                user=request.user,
                resource_id=resource_id
            )
        else:
            # Retirer la ressource cochée
            CheckedResource.objects.filter(
                user=request.user,
                resource_id=resource_id
            ).delete()
        
        return Response({
            'success': True,
            'resourceId': resource_id,
            'checked': checked
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'success': False, 
            'error': str(e)
        }, status=400)

# ==================== END OF FILE ====================