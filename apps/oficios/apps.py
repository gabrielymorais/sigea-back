from django.apps import AppConfig


class OficiosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.oficios"

    def ready(self):
        from . import signals  # noqa