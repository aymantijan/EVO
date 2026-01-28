from django.urls import path
from . import views

app_name = 'actions'

urlpatterns = [
    path('', views.actions_view, name='actions'),
]
