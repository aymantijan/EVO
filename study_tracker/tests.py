from django.test import TestCase
from django.contrib.auth.models import User
from .models import Subject, Chapter, Section


class StudyTrackerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.subject = Subject.objects.create(
            user_profile=self.user.profile,
            name='Mathematics'
        )
        self.chapter = Chapter.objects.create(
            subject=self.subject,
            title='Algebra',
            chapter_number=1
        )

    def test_section_progress(self):
        """Test progression des sections"""
        section = Section.objects.create(
            chapter=self.chapter,
            title='Equations',
            section_number=1
        )

        self.assertFalse(section.completed)
        self.assertEqual(self.subject.progress_percentage, 0)

        section.mark_completed()
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.progress_percentage, 2.0)
