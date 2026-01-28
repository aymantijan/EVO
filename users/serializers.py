from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Serialize User model"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serialize UserProfile model with nested user"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'level', 'total_xp',
            'hp_general', 'hp_physical', 'hp_mental', 'hp_social', 'hp_spiritual',
            'hp_global', 'current_streak', 'longest_streak',
            'last_action_date', 'bio', 'avatar', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']