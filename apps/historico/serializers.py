from rest_framework import serializers

from .models import HistoricoAcao


class HistoricoAcaoSerializer(serializers.ModelSerializer):
    acao_display = serializers.CharField(source="get_acao_display", read_only=True)
    modulo_display = serializers.CharField(source="get_modulo_display", read_only=True)

    class Meta:
        model = HistoricoAcao
        fields = [
            "id",
            "acao",
            "acao_display",
            "modulo",
            "modulo_display",
            "descricao",
            "objeto_id",
            "objeto_nome",
            "created_at",
        ]
        read_only_fields = fields
