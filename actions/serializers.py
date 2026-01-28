from rest_framework import serializers
from .models import Category, ActionTemplate, Action


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'color']


class ActionTemplateSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = ActionTemplate
        fields = ['id', 'category', 'category_name', 'name', 'description', 'xp_reward', 'is_active']


class ActionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Action
        fields = [
            'id', 'user', 'username', 'category', 'category_name',
            'template', 'template_name', 'title', 'description',
            'xp_earned', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']