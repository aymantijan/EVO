from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    """Cours d'étude"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='📚')
    color = models.CharField(max_length=7, default='#2ecc71')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ['name']

    def __str__(self):
        return self.name


class StudySession(models.Model):
    """Sessions d'étude"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='study_tracker_sessions'  # ← RENOMMÉ (unique)
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='study_tracker_user_sessions'  # ← RENOMMÉ (unique)
    )
    title = models.CharField(max_length=200)
    duration_minutes = models.IntegerField()
    notes = models.TextField(blank=True)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Session d'Étude"
        verbose_name_plural = "Sessions d'Étude"
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Progress(models.Model):
    """Progression dans un cours"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='study_tracker_progress'  # ← RENOMMÉ (unique)
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='study_tracker_user_progress'  # ← RENOMMÉ (unique)
    )
    completion_percentage = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Progression"
        verbose_name_plural = "Progressions"
        unique_together = ['user', 'course']
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.name} ({self.completion_percentage}%)"
