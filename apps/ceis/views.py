from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import CEI
from .serializers import CEISerializer


class CEIViewSet(viewsets.ModelViewSet):
    queryset = CEI.objects.all()
    serializer_class = CEISerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "inep",
        "nome_gestor",
        "bairro",
        "rua",
        "parecer_regulamentacao",
    ]
    ordering_fields = [
        "validade_regulamentacao",
        "updated_at",
        "created_at",
        "inep",
    ]
    ordering = ["-updated_at"]