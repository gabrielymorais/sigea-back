from django.apps import AppConfig


class AtasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.atas"

    def ready(self):
        from . import signals  
