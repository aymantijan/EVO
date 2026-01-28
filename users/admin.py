from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'phone', 'created_at']
    search_fields = ['user__username', 'location']
    list_filter = ['created_at', 'birth_date']
    readonly_fields = ['created_at', 'updated_at']
