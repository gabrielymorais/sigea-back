from django.apps import AppConfig


class PareceresConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pareceres"

    def ready(self):
        from . import signals  # noqa