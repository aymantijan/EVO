from django.db.models.signals import post_save
from django.dispatch import receiver
from actions.models import Action


@receiver(post_save, sender=Action)
def on_action_created(sender, instance, created, **kwargs):
    """Déclencher les checks quand une action est créée"""
    if created:
        from .services import check_achievements, update_challenge_progress

        profile = instance.user_profile

        # Check achievements
        check_achievements(profile)

        # Update challenge progress
        if instance.category:
            update_challenge_progress(profile, 'weekly', 1)
            update_challenge_progress(profile, 'monthly', 1)
