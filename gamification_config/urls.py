from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from gamification import views as gamification_views

urlpatterns = [
    # ====== ADMIN DJANGO ======
    path('admin/', admin.site.urls),

    # ====== REST FRAMEWORK ======
    path('api-auth/', include('rest_framework.urls')),

    # ====== AUTHENTICATION ======
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True,
        next_page='gamification:dashboard'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # ====== API ENDPOINTS - RESOURCES (AU NIVEAU RACINE) ======
    path('api/resources/', gamification_views.api_get_resources, name='api_get_resources'),
    path('api/resources/<str:res_type>/', gamification_views.api_get_resources_by_type, name='api_get_resources_by_type'),
    path('api/search/', gamification_views.api_search_resources, name='api_search_resources'),
    path('api/get-user-data/', gamification_views.api_get_user_data, name='api_get_user_data'),
    path('api/save-data/', gamification_views.api_save_challenge_data, name='api_save_challenge_data'),
    path('api/add-block/', gamification_views.api_add_time_block, name='api_add_time_block'),
    path('api/toggle-block/', gamification_views.api_toggle_time_block, name='api_toggle_time_block'),
    path('api/validate-day/', gamification_views.api_validate_day, name='api_validate_day'),
    path('api/evaluate/', gamification_views.api_evaluate_activity, name='api_evaluate_activity'),

    # ====== GAMIFICATION APP ======
    path('', include('gamification.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)