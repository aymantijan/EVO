from datetime import timedelta
from django.utils import timezone
from .models import Achievement, UserAchievement, Challenge, UserChallenge


def check_achievements(user_profile):
    """Vérifier et débloquer les achievements"""
    achievements = Achievement.objects.filter(
        condition_type__in=['xp', 'level', 'streak']
    )

    for achievement in achievements:
        if UserAchievement.objects.filter(
                user_profile=user_profile,
                achievement=achievement
        ).exists():
            continue

        unlocked = False

        if achievement.condition_type == 'xp':
            if user_profile.total_xp >= achievement.condition_value:
                unlocked = True

        elif achievement.condition_type == 'level':
            if user_profile.level >= achievement.condition_value:
                unlocked = True

        elif achievement.condition_type == 'streak':
            if user_profile.current_streak >= achievement.condition_value:
                unlocked = True

        if unlocked:
            UserAchievement.objects.create(
                user_profile=user_profile,
                achievement=achievement
            )


def update_challenge_progress(user_profile, challenge_type, value_to_add=1):
    """Mettre à jour la progression des challenges"""
    active_challenges = UserChallenge.objects.filter(
        user_profile=user_profile,
        challenge__challenge_type=challenge_type,
        completed=False,
        challenge__is_active=True
    )

    for user_challenge in active_challenges:
        user_challenge.progress += value_to_add

        if user_challenge.progress >= user_challenge.challenge.target_value:
            user_challenge.completed = True
            user_challenge.completed_at = timezone.now()

            # Attribuer récompenses
            user_profile.total_xp += user_challenge.challenge.xp_reward

            # Bonus HP
            for hp_type, value in user_challenge.challenge.hp_rewards.items():
                setattr(user_profile, f'{hp_type}_hp',
                        min(100, getattr(user_profile, f'{hp_type}_hp') + value))

            user_profile.save()

        user_challenge.save()
