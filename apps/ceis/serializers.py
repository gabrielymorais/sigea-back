from rest_framework import serializers
from .models import CEI


class CEISerializer(serializers.ModelSerializer):
    class Meta:
        model = CEI
        fields = [
            "id",
            "inep",
            "nome_gestor",
            "parecer_regulamentacao",
            "validade_regulamentacao",
            "bairro",
            "rua",
            "numero",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_inep(self, value: str):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("INEP é obrigatório.")
        return value