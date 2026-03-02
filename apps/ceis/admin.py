from django.contrib import admin
from .models import CEI


@admin.register(CEI)
class CEIAdmin(admin.ModelAdmin):
    list_display = ("inep", "nome_gestor", "bairro", "rua", "numero", "validade_regulamentacao")
    search_fields = ("inep", "nome_gestor", "bairro", "rua", "parecer_regulamentacao")
    list_filter = ("bairro",)