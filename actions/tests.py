from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, ActionTemplate, Action


class ActionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='physical',
            display_name='Santé Physique',
            description='Actions liées à la santé physique',
            icon='heart'
        )

    def test_create_action(self):
        """Créer une action"""
        action = Action.objects.create(
            user_profile=self.user.profile,
            category=self.category,
            title='Test Action',
            xp_earned=50,
            physical_hp_change=10
        )
        self.assertEqual(action.title, 'Test Action')
        self.assertEqual(action.xp_earned, 50)
