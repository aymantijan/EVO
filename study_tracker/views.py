from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Subject, Chapter, Section, StudySession, StudyGoal, StudyStreak
from .serializers import SubjectSerializer, ChapterSerializer, SectionSerializer, StudySessionSerializer, StudyGoalSerializer, StudyStreakSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    """Subject viewset"""
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['-created_at', 'name']

    def get_queryset(self):
        return Subject.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChapterViewSet(viewsets.ModelViewSet):
    """Chapter viewset"""
    serializer_class = ChapterSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['subject']
    ordering_fields = ['number', '-created_at']

    def get_queryset(self):
        return Chapter.objects.filter(subject__user=self.request.user)


class SectionViewSet(viewsets.ModelViewSet):
    """Section viewset"""
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['chapter', 'is_completed']
    ordering_fields = ['number', '-created_at']

    def get_queryset(self):
        return Section.objects.filter(chapter__subject__user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_completed(self, request, pk=None):
        """Mark section as completed"""
        section = self.get_object()
        if section.mark_completed():
            return Response({'status': 'section marked as completed'})
        return Response({'status': 'section already completed'}, status=status.HTTP_400_BAD_REQUEST)


class StudySessionViewSet(viewsets.ModelViewSet):
    """Study session viewset"""
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['subject', 'difficulty']
    ordering_fields = ['-created_at', 'duration_minutes']

    def get_queryset(self):
        return StudySession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudyGoalViewSet(viewsets.ModelViewSet):
    """Study goal viewset"""
    serializer_class = StudyGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['subject', 'status']
    ordering_fields = ['-start_date', 'status']

    def get_queryset(self):
        return StudyGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudyStreakViewSet(viewsets.ModelViewSet):
    """Study streak viewset"""
    serializer_class = StudyStreakSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['subject']
    ordering_fields = ['-current_streak', '-longest_streak']

    def get_queryset(self):
        return StudyStreak.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def update_streak(self, request, pk=None):
        """Update streak for subject"""
        streak = self.get_object()
        streak.update_streak()
        serializer = self.get_serializer(streak)
        return Response(serializer.data)