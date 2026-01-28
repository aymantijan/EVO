from django.apps import AppConfig


class StudyTrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'study_tracker'

    def ready(self):
        pass
        #from . import signals
