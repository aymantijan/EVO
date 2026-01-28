from django.contrib import admin
from .models import Category, Action


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'category', 'created_at']
    search_fields = ['user__username', 'action_type']
    list_filter = ['action_type', 'category', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
