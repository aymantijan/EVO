from django.urls import path
from . import views

app_name = 'study_tracker'

urlpatterns = [
    path('', views.study_tracker_view, name='study_tracker'),
]
