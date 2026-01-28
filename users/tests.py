from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_profile_created(self):
        """Profile créé automatiquement"""
        self.assertTrue(hasattr(self.user, 'profile'))

    def test_hp_global_calculation(self):
        """Calcul du HP global"""
        profile = self.user.profile
        profile.physical_hp = 100
        profile.mental_hp = 80
        profile.social_hp = 60
        profile.productivity_hp = 90
        profile.creativity_hp = 70
        expected = (100 + 80 + 60 + 90 + 70) / 5
        self.assertEqual(profile.hp_global, expected)

    def test_add_xp(self):
        """Ajouter XP"""
        profile = self.user.profile
        initial_xp = profile.total_xp
        profile.add_xp(100)
        self.assertEqual(profile.total_xp, initial_xp + 100)

    def test_level_update(self):
        """Mise à jour du niveau"""
        profile = self.user.profile
        profile.total_xp = 2500
        profile.update_level()
        self.assertEqual(profile.level, 2)
