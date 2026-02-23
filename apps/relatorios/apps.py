from django.apps import AppConfig


class RelatoriosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.relatorios"

    def ready(self):
        from . import signals  
