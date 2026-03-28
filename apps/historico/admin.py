from django.contrib import admin

from .models import HistoricoAcao


@admin.register(HistoricoAcao)
class HistoricoAcaoAdmin(admin.ModelAdmin):
    list_display = ["usuario", "acao", "modulo", "descricao", "objeto_nome", "created_at"]
    list_filter = ["acao", "modulo", "created_at"]
    search_fields = ["usuario__username", "usuario__email", "descricao", "objeto_nome"]
    readonly_fields = ["usuario", "acao", "modulo", "descricao", "objeto_id", "objeto_nome", "created_at"]
    ordering = ["-created_at"]
