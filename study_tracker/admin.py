from django.contrib import admin
from .models import Course, StudySession, Progress


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'title', 'duration_minutes', 'started_at']
    search_fields = ['user__username', 'title']
    list_filter = ['course', 'started_at']
    readonly_fields = ['created_at']


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'completion_percentage', 'is_completed']
    search_fields = ['user__username', 'course__name']
    list_filter = ['course', 'is_completed']
    readonly_fields = ['started_at']
