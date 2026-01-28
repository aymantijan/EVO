from django.urls import path, include

urlpatterns = [
    path('', include('users.urls')),
    path('', include('actions.urls')),
    path('', include('gamification.urls')),
    path('', include('study_tracker.urls')),
]
