import io
import os
import zipfile
import tempfile
import subprocess
from pathlib import Path

from django.http import FileResponse, HttpResponse

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
)

from .models import ParecerFolder, ParecerFile
from .serializers import ParecerFolderSerializer, ParecerFileSerializer
from apps.historico.utils import registrar_acao
from apps.historico.models import TipoAcao, Modulo


def _safe_filename(name: str) -> str:
    name = name or "arquivo"
    return "".join(
        c for c in name if c.isalnum() or c in (" ", "-", "_", ".", "(", ")", "[", "]")
    ).strip()


def _convert_to_pdf_with_libreoffice(input_path: str) -> str:
    input_path = str(input_path)
    in_dir = str(Path(input_path).parent)
    base = Path(input_path).stem
    out_pdf = str(Path(in_dir) / f"{base}.pdf")

    cmd = [
        "soffice",
        "--headless",
        "--nologo",
        "--nolockcheck",
        "--norestore",
        "--convert-to",
        "pdf",
        "--outdir",
        in_dir,
        input_path,
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=40,
    )

    if result.returncode != 0 or not os.path.exists(out_pdf):
        raise RuntimeError(f"Falha na conversão para PDF. stderr={result.stderr[:500]}")

    return out_pdf


@extend_schema_view(
    list=extend_schema(
        summary="Listar pastas de PARECERES do usuário",
        parameters=[
            OpenApiParameter(name="q", type=str, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(name="name", type=str, location=OpenApiParameter.QUERY, required=False),
        ],
    ),
    retrieve=extend_schema(summary="Detalhar uma pasta de PARECERES"),
    create=extend_schema(
        summary="Criar uma pasta de PARECERES",
        examples=[OpenApiExample(name="Criar pasta", value={"name": "Pareceres - 2026"}, request_only=True)],
    ),
    partial_update=extend_schema(
        summary="Atualizar parcialmente uma pasta de PARECERES",
        examples=[OpenApiExample(name="Renomear pasta", value={"name": "Pareceres - 2026 (Final)"}, request_only=True)],
    ),
    destroy=extend_schema(summary="Excluir uma pasta de PARECERES"),
)
class ParecerFolderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ParecerFolderSerializer

    def get_queryset(self):
        qs = ParecerFolder.objects.filter(owner=self.request.user)

        q = (self.request.query_params.get("q") or "").strip()
        name = (self.request.query_params.get("name") or "").strip()
        term = q or name
        if term:
            qs = qs.filter(name__icontains=term)

        return qs

    def perform_create(self, serializer):
        folder = serializer.save(owner=self.request.user)
        registrar_acao(
            usuario=self.request.user,
            acao=TipoAcao.CRIAR,
            modulo=Modulo.PARECERES,
            descricao=f'Criou a pasta "{folder.name}"',
            objeto_id=folder.pk,
            objeto_nome=folder.name,
        )

    def perform_update(self, serializer):
        folder = serializer.save()
        registrar_acao(
            usuario=self.request.user,
            acao=TipoAcao.EDITAR,
            modulo=Modulo.PARECERES,
            descricao=f'Editou a pasta "{folder.name}"',
            objeto_id=folder.pk,
            objeto_nome=folder.name,
        )

    def perform_destroy(self, instance):
        registrar_acao(
            usuario=self.request.user,
            acao=TipoAcao.EXCLUIR,
            modulo=Modulo.PARECERES,
            descricao=f'Excluiu a pasta "{instance.name}"',
            objeto_id=instance.pk,
            objeto_nome=instance.name,
        )
        instance.delete()

    @extend_schema(
        summary="Enviar múltiplos arquivos para uma pasta de PARECERES",
        responses={
            201: ParecerFileSerializer(many=True),
            400: OpenApiResponse(description="Nenhum arquivo enviado no campo `files`."),
        },
    )
    @action(detail=True, methods=["post"], url_path="files")
    def upload_files(self, request, pk=None):
        folder = self.get_object()
        files = request.FILES.getlist("files")

        if not files:
            return Response(
                {"detail": "Envie ao menos um arquivo no campo 'files'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created = []
        for f in files:
            created.append(ParecerFile.objects.create(folder=folder, file=f, original_name=f.name))

        nomes = ", ".join(f.name for f in files)
        registrar_acao(
            usuario=request.user,
            acao=TipoAcao.UPLOAD,
            modulo=Modulo.PARECERES,
            descricao=f'Fez upload de {len(files)} arquivo(s) na pasta "{folder.name}": {nomes}'[:500],
            objeto_id=folder.pk,
            objeto_nome=folder.name,
        )

        serializer = ParecerFileSerializer(created, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Baixar uma pasta de PARECERES completa (ZIP)")
    @action(detail=True, methods=["get"], url_path="download")
    def download_folder(self, request, pk=None):
        folder = self.get_object()
        files_qs = folder.files.all()

        if not files_qs.exists():
            return Response(
                {"detail": "Esta pasta não possui arquivos para download."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for item in files_qs:
                if not item.file:
                    continue
                arcname = item.original_name or item.file.name.split("/")[-1]
                with item.file.open("rb") as fp:
                    zf.writestr(arcname, fp.read())

        buffer.seek(0)

        safe_name = "".join(c for c in folder.name if c.isalnum() or c in (" ", "-", "_")).strip()
        zip_filename = f"{safe_name or 'pasta_parecer'}_{folder.id}.zip"

        registrar_acao(
            usuario=request.user,
            acao=TipoAcao.DOWNLOAD,
            modulo=Modulo.PARECERES,
            descricao=f'Baixou a pasta "{folder.name}" em ZIP',
            objeto_id=folder.pk,
            objeto_nome=folder.name,
        )

        resp = HttpResponse(buffer.getvalue(), content_type="application/zip")
        resp["Content-Disposition"] = f'attachment; filename="{zip_filename}"'
        return resp


@extend_schema_view(
    list=extend_schema(
        summary="Listar arquivos de PARECERES",
        parameters=[
            OpenApiParameter(name="folder_id", type=int, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(name="q", type=str, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(name="name", type=str, location=OpenApiParameter.QUERY, required=False),
        ],
    ),
    retrieve=extend_schema(summary="Detalhar um arquivo de PARECER"),
    partial_update=extend_schema(
        summary="Renomear um arquivo de PARECER",
        examples=[OpenApiExample(name="Renomear arquivo", value={"original_name": "Parecer - Final.pdf"}, request_only=True)],
    ),
)
class ParecerFileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ParecerFileSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        qs = ParecerFile.objects.filter(folder__owner=self.request.user)

        folder_id = (self.request.query_params.get("folder_id") or "").strip()
        if folder_id:
            qs = qs.filter(folder_id=folder_id)

        q = (self.request.query_params.get("q") or "").strip()
        name = (self.request.query_params.get("name") or "").strip()
        term = q or name
        if term:
            qs = qs.filter(original_name__icontains=term)

        return qs

    @extend_schema(summary="Pré-visualizar um arquivo como PDF (com conversão)")
    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, pk=None):
        obj = self.get_object()

        if not obj.file:
            return Response({"detail": "Arquivo não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        filename = (obj.original_name or obj.file.name or "").lower()
        ext = Path(filename).suffix.lower().lstrip(".")
        allowed_office = {"doc", "docx", "ppt", "pptx", "xls", "xlsx"}
        is_pdf = ext == "pdf"

        if is_pdf:
            resp = FileResponse(obj.file.open("rb"), content_type="application/pdf")
            resp["Content-Disposition"] = f'inline; filename="{_safe_filename(obj.original_name or "preview.pdf")}"'
            return resp

        if ext in allowed_office:
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    src_name = _safe_filename(obj.original_name or f"arquivo.{ext}")
                    src_path = str(Path(tmpdir) / src_name)

                    with obj.file.open("rb") as fin, open(src_path, "wb") as fout:
                        fout.write(fin.read())

                    pdf_path = _convert_to_pdf_with_libreoffice(src_path)
                    with open(pdf_path, "rb") as pdf_fp:
                        pdf_bytes = pdf_fp.read()

                resp = HttpResponse(pdf_bytes, content_type="application/pdf")
                resp["Content-Disposition"] = f'inline; filename="{_safe_filename(Path(src_name).stem)}.pdf"'
                return resp
            except subprocess.TimeoutExpired:
                return Response(
                    {"detail": "Tempo excedido ao converter o arquivo para PDF."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            except Exception:
                return Response(
                    {"detail": "Falha ao converter o arquivo para PDF."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {"detail": "Tipo de arquivo não suportado para preview."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(summary="Baixar um arquivo de PARECER (download protegido)")
    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        obj = self.get_object()

        if not obj.file:
            return Response({"detail": "Arquivo não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        filename = obj.original_name or obj.file.name.split("/")[-1]
        registrar_acao(
            usuario=request.user,
            acao=TipoAcao.DOWNLOAD,
            modulo=Modulo.PARECERES,
            descricao=f'Baixou o arquivo "{obj.original_name}" da pasta "{obj.folder.name}"',
            objeto_id=obj.pk,
            objeto_nome=obj.original_name,
        )
        return FileResponse(obj.file.open("rb"), as_attachment=True, filename=filename)


@extend_schema_view(
    destroy=extend_schema(summary="Excluir um arquivo de uma pasta de PARECER"),
)
class ParecerFileDeleteViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def destroy(self, request, pk=None):
        try:
            obj = ParecerFile.objects.get(id=pk, folder__owner=request.user)
        except ParecerFile.DoesNotExist:
            return Response({"detail": "Arquivo não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        registrar_acao(
            usuario=request.user,
            acao=TipoAcao.EXCLUIR,
            modulo=Modulo.PARECERES,
            descricao=f'Excluiu o arquivo "{obj.original_name}" da pasta "{obj.folder.name}"',
            objeto_id=obj.pk,
            objeto_nome=obj.original_name,
        )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)