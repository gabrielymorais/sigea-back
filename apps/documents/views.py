from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Document
from .serializers import DocumentSerializer


@extend_schema_view(
    list=extend_schema(tags=["Documents"], summary="Listar documentos"),
    create=extend_schema(tags=["Documents"], summary="Criar documento (upload)"),
    retrieve=extend_schema(tags=["Documents"], summary="Detalhar documento"),
    update=extend_schema(tags=["Documents"], summary="Atualizar documento"),
    partial_update=extend_schema(tags=["Documents"], summary="Atualizar parcialmente"),
    destroy=extend_schema(tags=["Documents"], summary="Excluir documento"),
)
class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
