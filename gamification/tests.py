from django.test import TestCase
from django.contrib.auth.models import User
from .models import Achievement, Challenge
from .services import check_achievements


class AchievementTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.achievement = Achievement.objects.create(
            name='First Steps',
            description='Earn 100 XP',
            icon='star',
            xp_threshold=100,
            condition_type='xp',
            condition_value=100
        )

    def test_achievement_unlock(self):
        """Débloquer un achievement"""
        profile = self.user.profile
        profile.total_xp = 100
        profile.save()

        check_achievements(profile)

        self.assertTrue(
            profile.achievements.filter(achievement=self.achievement).exists()
        )
