from django.contrib import admin
from .models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("inep", "nome_gestor", "bairro", "rua", "numero", "validade_regulamentacao")
    search_fields = ("inep", "nome_gestor", "bairro", "rua", "parecer_regulamentacao")
    list_filter = ("bairro",)
