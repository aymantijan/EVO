from rest_framework import serializers
from .models import Subject, Chapter, Section, StudySession, StudyGoal, StudyStreak


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'chapter', 'number', 'title', 'description', 'is_completed', 'completed_at', 'created_at',
                  'updated_at']


class ChapterSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ['id', 'subject', 'number', 'title', 'description', 'progress', 'sections', 'created_at', 'updated_at']

    def get_progress(self, obj):
        return obj.progress


class SubjectSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    total_progress = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'user', 'username', 'name', 'description', 'icon', 'color', 'total_progress', 'chapters',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_total_progress(self, obj):
        return obj.total_progress


class StudySessionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    section_title = serializers.CharField(source='section.title', read_only=True)

    class Meta:
        model = StudySession
        fields = ['id', 'user', 'username', 'subject', 'subject_name', 'section', 'section_title', 'duration_minutes',
                  'difficulty', 'notes', 'xp_earned', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class StudyGoalSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = StudyGoal
        fields = ['id', 'user', 'username', 'subject', 'subject_name', 'title', 'description', 'target_chapters',
                  'completed_chapters', 'progress_percentage', 'status', 'start_date', 'target_date', 'completed_date']
        read_only_fields = ['id', 'user']

    def get_progress_percentage(self, obj):
        return obj.progress_percentage


class StudyStreakSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = StudyStreak
        fields = ['id', 'user', 'username', 'subject', 'subject_name', 'current_streak', 'longest_streak',
                  'last_study_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']