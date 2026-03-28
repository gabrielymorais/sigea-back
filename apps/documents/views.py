import os
import mimetypes

from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Document
from .serializers import DocumentSerializer
from apps.historico.utils import registrar_acao
from apps.historico.models import TipoAcao, Modulo


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

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "doc_type"]
    ordering_fields = ["updated_at", "created_at", "name", "doc_type"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        doc = serializer.save(owner=self.request.user)
        registrar_acao(
            usuario=self.request.user,
            acao=TipoAcao.UPLOAD,
            modulo=Modulo.DOCUMENTOS,
            descricao=f'Enviou o documento "{doc.name}"',
            objeto_id=doc.pk,
            objeto_nome=doc.name,
        )

    def perform_update(self, serializer):
        doc = serializer.save()
        registrar_acao(
            usuario=self.request.user,
            acao=TipoAcao.EDITAR,
            modulo=Modulo.DOCUMENTOS,
            descricao=f'Editou o documento "{doc.name}"',
            objeto_id=doc.pk,
            objeto_nome=doc.name,
        )

    def perform_destroy(self, instance):
        registrar_acao(
            usuario=self.request.user,
            acao=TipoAcao.EXCLUIR,
            modulo=Modulo.DOCUMENTOS,
            descricao=f'Excluiu o documento "{instance.name}"',
            objeto_id=instance.pk,
            objeto_nome=instance.name,
        )
        instance.delete()

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        doc = self.get_object()

        if not doc.file:
            return Response(
                {"detail": "Documento sem arquivo associado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        doc.file.open("rb")

        filename = os.path.basename(doc.file.name) or f"documento-{doc.pk}"
        content_type, _ = mimetypes.guess_type(filename)
        content_type = content_type or "application/octet-stream"

        registrar_acao(
            usuario=request.user,
            acao=TipoAcao.DOWNLOAD,
            modulo=Modulo.DOCUMENTOS,
            descricao=f'Baixou o documento "{doc.name}"',
            objeto_id=doc.pk,
            objeto_nome=doc.name,
        )
        return FileResponse(
            doc.file,
            as_attachment=True,
            filename=filename,
            content_type=content_type,
        )

    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, pk=None):
        doc = self.get_object()

        if not doc.file:
            return Response(
                {"detail": "Documento sem arquivo associado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        doc.file.open("rb")

        filename = os.path.basename(doc.file.name) or f"documento-{doc.pk}"
        content_type, _ = mimetypes.guess_type(filename)
        content_type = content_type or "application/octet-stream"

        return FileResponse(
            doc.file,
            as_attachment=False,
            filename=filename,
            content_type=content_type,
        )