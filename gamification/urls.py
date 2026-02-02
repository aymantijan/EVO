from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    # ==================== PAGES ====================

    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('challenges/', views.ChallengesView.as_view(), name='challenges'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('skills/', views.SkillsView.as_view(), name='skills'),
    path('skills-page/', views.skills_page, name='skills_page'),
    path('achievements/', views.AchievementsView.as_view(), name='achievements'),
    path('study-tracker/', views.StudyTrackerView.as_view(), name='study_tracker'),
    path('actions/', views.ActionsView.as_view(), name='actions'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # ==================== API - UPLOAD IMAGES ====================

    path('api/upload-profile-image/', views.api_upload_profile_image, name='api_upload_profile_image'),
    path('api/upload-cover-image/', views.api_upload_cover_image, name='api_upload_cover_image'),
    
    # ✅ NOUVELLE ROUTE AJOUTÉE - Pour charger les images au démarrage
    path('api/get-profile-images/', views.api_get_profile_images, name='api_get_profile_images'),

    # ==================== API - GET DATA (SOURCE UNIQUE DE VÉRITÉ) ====================

    path('api/get-user-data/', views.api_get_user_data, name='api_get_user_data'),

    # ==================== API - DAILY ACTIVITIES & STREAK ====================

    path('api/save-daily-activity/', views.api_save_daily_activity, name='api_save_daily_activity'),
    path('api/get-streak/', views.api_get_streak, name='api_get_streak'),

    # ==================== API - IA EVALUATION ====================

    path('api/evaluate-activity/', views.api_evaluate_activity, name='api_evaluate_activity'),
    path('api/confirm-evaluation/', views.api_confirm_evaluation, name='api_confirm_evaluation'),

    # ==================== API - LEGACY (COMPATIBILITY) ====================

    path('api/save-challenge-data/', views.api_save_challenge_data, name='api_save_challenge_data'),
    path('api/add-time-block/', views.api_add_time_block, name='api_add_time_block'),
    path('api/toggle-time-block/', views.api_toggle_time_block, name='api_toggle_time_block'),
    path('api/validate-day/', views.api_validate_day, name='api_validate_day'),
    path('api/validate-day-planning/', views.api_validate_day_planning, name='api_validate_day_planning'),

    # ==================== API - SKILLS ====================

    path('api/add-skill/', views.add_skill, name='add_skill'),
    path('api/add-category/', views.add_category, name='add_category'),
    path('api/add-domain/', views.add_domain, name='add_domain'),
    path('api/skills/', views.get_user_skills, name='api_user_skills'),
    path('api/skills/<int:skill_id>/', views.get_skill_details, name='api_skill_details'),
    path('api/domain-progress/<str:domain>/', views.get_domain_progress, name='api_domain_progress'),
    path('api/remove-skill/', views.remove_skill, name='remove_skill'),
    path('api/remove-category/', views.remove_category, name='remove_category'),
    path('api/remove-domain/', views.remove_domain, name='remove_domain'),

    # ==================== API - PROFILE ====================

    path('api/profile/', views.get_profile, name='api_get_profile'),
    path('api/profile/update/', views.update_profile, name='api_update_profile'),

    # ==================== API - LEADERBOARD ====================

    path('api/leaderboard/', views.get_leaderboard, name='api_leaderboard'),
    path('api/leaderboard/weekly/', views.get_leaderboard_weekly, name='api_leaderboard_weekly'),
    path('api/leaderboard/monthly/', views.get_leaderboard_monthly, name='api_leaderboard_monthly'),
    path('api/leaderboard/simple/', views.get_leaderboard_simple, name='api_leaderboard_simple'),
    path('api/leaderboard/user-rank/', views.get_user_rank, name='api_user_rank'),

    # ==================== API - ACHIEVEMENTS ====================

    path('api/achievements/', views.get_user_achievements, name='api_user_achievements'),

    # ==================== API - CHALLENGES ====================

    path('api/challenges/active/', views.get_active_challenges, name='api_active_challenges'),
    path('api/challenges/<int:challenge_id>/complete/', views.complete_challenge, name='api_complete_challenge'),

    # ==================== API - STUDY SESSIONS ====================

    path('api/study-sessions/', views.get_study_sessions, name='api_study_sessions'),
    path('api/study-sessions/create/', views.create_study_session, name='api_create_study_session'),

    # ==================== API - DASHBOARD ====================

    path('api/dashboard/stats/', views.get_dashboard_stats, name='api_dashboard_stats'),

    # ==================== API - RESOURCES ====================

    path('api/resources/all/', views.api_get_all_resources, name='api_resources_all'),
    path('api/resources/', views.api_get_resources, name='api_resources'),
    path('api/resources/<str:resource_type>/', views.api_get_resources_by_type, name='api_resources_by_type'),
    path('api/resources/search/', views.api_search_resources, name='api_search_resources'),

    # ==================== API - STUDY TRACKER ====================

    path('api/study-tracker/subjects/', views.get_study_subjects, name='api_study_subjects'),
    path('api/study-tracker/subjects/create/', views.create_study_subject, name='api_create_study_subject'),
    path('api/study-tracker/subjects/<int:subject_id>/delete/', views.delete_study_subject, name='api_delete_study_subject'),

    path('api/study-tracker/chapters/', views.get_study_chapters, name='api_study_chapters'),
    path('api/study-tracker/chapters/create/', views.create_study_chapter, name='api_create_study_chapter'),
    path('api/study-tracker/chapters/<int:chapter_id>/delete/', views.delete_study_chapter, name='api_delete_study_chapter'),

    path('api/study-tracker/sections/', views.get_study_sections, name='api_study_sections'),
    path('api/study-tracker/sections/create/', views.create_study_section, name='api_create_study_section'),
    path('api/study-tracker/sections/<int:section_id>/', views.update_study_section, name='api_update_study_section'),
    path('api/study-tracker/sections/<int:section_id>/delete/', views.delete_study_section, name='api_delete_study_section'),
]