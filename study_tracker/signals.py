from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Section, StudyGoal, StudySession


@receiver(post_save, sender=Section)
def section_completed_signal(sender, instance, created, **kwargs):
    """Déclencher automatiquement quand une section est complétée"""
    if instance.completed and not created:
        from actions.models import Action, Category

        category, _ = Category.objects.get_or_create(name='productivity')

        Action.objects.create(
            user_profile=instance.chapter.subject.user_profile,
            category=category,
            title=f"Section complétée: {instance.title}",
            description=f"Chapitre {instance.chapter.chapter_number}: {instance.chapter.title}",
            xp_earned=50,
            productivity_hp_change=5,
            creativity_hp_change=2,
            action_date=timezone.now().date()
        )


@receiver(post_save, sender=StudyGoal)
def goal_achieved_signal(sender, instance, created, **kwargs):
    """Quand un objectif est atteint, attribuer récompense"""
    if instance.achieved and not created:
        profile = instance.user_profile
        profile.total_xp += instance.xp_reward
        profile.mental_hp = min(100, profile.mental_hp + 10)
        profile.productivity_hp = min(100, profile.productivity_hp + 15)
        profile.save()
        profile.update_level()


@receiver(post_save, sender=StudySession)
def session_created_signal(sender, instance, created, **kwargs):
    """Mettre à jour les streaks quand une session est créée"""
    if created:
        from .models import StudyStreak

        streak, _ = StudyStreak.objects.get_or_create(
            user_profile=instance.user_profile,
            subject=instance.subject
        )
        streak.update_streak(instance.start_time.date())
