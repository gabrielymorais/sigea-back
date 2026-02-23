from django.apps import AppConfig


class ReaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.rea"

    def ready(self):
        from . import signals  # noqa