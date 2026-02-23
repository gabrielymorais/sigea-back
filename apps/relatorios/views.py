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

from .models import ReportFolder, ReportFile
from .serializers import ReportFolderSerializer, ReportFileSerializer


def _safe_filename(name: str) -> str:
    name = name or "arquivo"
    return "".join(
        c for c in name if c.isalnum() or c in (" ", "-", "_", ".", "(", ")", "[", "]")
    ).strip()


def _convert_to_pdf_with_libreoffice(input_path: str) -> str:
    """
    Converte o arquivo em `input_path` para PDF usando LibreOffice (soffice).
    Retorna o caminho do PDF gerado.
    """
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
        summary="Listar pastas de RELATÓRIOS do usuário",
        description=(
            "Retorna todas as pastas de RELATÓRIOS criadas pelo usuário autenticado. "
            "A resposta inclui os arquivos associados a cada pasta.\n\n"
            "Suporta pesquisa por nome via query params:\n"
            "- ?q=termo (recomendado)\n"
            "- ?name=termo (alias)"
        ),
        parameters=[
            OpenApiParameter(
                name="q",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Termo para filtrar pastas pelo nome (name__icontains).",
            ),
            OpenApiParameter(
                name="name",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Alias de `q`. Filtra pastas pelo nome (name__icontains).",
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Detalhar uma pasta de RELATÓRIOS",
        description=(
            "Retorna os dados de uma pasta específica do usuário autenticado, "
            "incluindo a lista de arquivos vinculados."
        ),
    ),
    create=extend_schema(
        summary="Criar uma pasta de RELATÓRIOS",
        description=(
            "Cria uma nova pasta de RELATÓRIOS para o usuário autenticado. "
            "Após criar a pasta, use a rota de upload múltiplo para anexar arquivos."
        ),
        examples=[
            OpenApiExample(
                name="Criar pasta",
                value={"name": "Relatórios - Fevereiro"},
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Atualizar uma pasta de RELATÓRIOS (substituição completa)",
        description="Atualiza completamente os dados da pasta (ex.: renomear).",
    ),
    partial_update=extend_schema(
        summary="Atualizar parcialmente uma pasta de RELATÓRIOS",
        description="Atualiza parcialmente os dados da pasta (ex.: renomear).",
        examples=[
            OpenApiExample(
                name="Renomear pasta",
                value={"name": "Relatórios - Fevereiro (Final)"},
                request_only=True,
            )
        ],
    ),
    destroy=extend_schema(
        summary="Excluir uma pasta de RELATÓRIOS",
        description=(
            "Exclui uma pasta de RELATÓRIOS do usuário autenticado. "
            "Os registros dos arquivos vinculados são removidos por cascade e, "
            "se configurado, o arquivo físico também é apagado do storage."
        ),
    ),
)
class ReportFolderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportFolderSerializer

    def get_queryset(self):
        qs = ReportFolder.objects.filter(owner=self.request.user)

        q = (self.request.query_params.get("q") or "").strip()
        name = (self.request.query_params.get("name") or "").strip()
        term = q or name

        if term:
            qs = qs.filter(name__icontains=term)

        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        summary="Enviar múltiplos arquivos para uma pasta de RELATÓRIOS",
        description=(
            "Faz upload de múltiplos arquivos e os vincula a uma pasta específica. "
            "Envie como multipart/form-data com o campo `files` podendo aparecer várias vezes.\n\n"
            "Exemplo no front:\n"
            "- formData.append('files', file1)\n"
            "- formData.append('files', file2)"
        ),
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID da pasta de RELATÓRIOS que receberá os arquivos.",
            )
        ],
        responses={
            201: ReportFileSerializer(many=True),
            400: OpenApiResponse(description="Nenhum arquivo enviado no campo `files`."),
            401: OpenApiResponse(description="Não autenticado."),
            404: OpenApiResponse(description="Pasta não encontrada (ou não pertence ao usuário)."),
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
            obj = ReportFile.objects.create(folder=folder, file=f, original_name=f.name)
            created.append(obj)

        serializer = ReportFileSerializer(created, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Baixar uma pasta de RELATÓRIOS completa (ZIP)",
        description=(
            "Gera e retorna um arquivo .zip contendo todos os arquivos cadastrados na pasta. "
            "Acesso protegido: apenas o usuário dono da pasta pode baixar."
        ),
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID da pasta de RELATÓRIOS que será baixada em formato .zip.",
            )
        ],
        responses={
            200: OpenApiResponse(description="ZIP gerado com sucesso."),
            400: OpenApiResponse(description="Pasta sem arquivos para download."),
            401: OpenApiResponse(description="Não autenticado."),
            404: OpenApiResponse(description="Pasta não encontrada (ou não pertence ao usuário)."),
        },
    )
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
        zip_filename = f"{safe_name or 'pasta_relatorio'}_{folder.id}.zip"

        resp = HttpResponse(buffer.getvalue(), content_type="application/zip")
        resp["Content-Disposition"] = f'attachment; filename="{zip_filename}"'
        return resp


@extend_schema_view(
    list=extend_schema(
        summary="Listar arquivos de RELATÓRIOS",
        description=(
            "Lista arquivos de RELATÓRIOS pertencentes ao usuário autenticado.\n\n"
            "Filtros suportados:\n"
            "- ?folder_id=ID (filtra arquivos de uma pasta específica)\n"
            "- ?q=termo (recomendado)\n"
            "- ?name=termo (alias)"
        ),
        parameters=[
            OpenApiParameter(
                name="folder_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filtra os arquivos por pasta (folder_id).",
            ),
            OpenApiParameter(
                name="q",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Termo para filtrar arquivos pelo nome original (original_name__icontains).",
            ),
            OpenApiParameter(
                name="name",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Alias de `q`. Filtra arquivos por original_name (icontains).",
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Detalhar um arquivo de RELATÓRIO",
        description="Retorna os dados de um arquivo específico pertencente ao usuário autenticado.",
    ),
    partial_update=extend_schema(
        summary="Renomear um arquivo de RELATÓRIO",
        description=(
            "Atualiza o nome exibido do arquivo (campo `original_name`). "
            "O arquivo físico no storage não é renomeado, apenas o nome mostrado no sistema."
        ),
        examples=[
            OpenApiExample(
                name="Renomear arquivo",
                value={"original_name": "Relatório - Final.pdf"},
                request_only=True,
            )
        ],
    ),
)
class ReportFileViewSet(viewsets.ModelViewSet):
    """
    Arquivos de RELATÓRIOS: listagem, detalhe, renomear (PATCH), preview e download protegido.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReportFileSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        qs = ReportFile.objects.filter(folder__owner=self.request.user)

        folder_id = (self.request.query_params.get("folder_id") or "").strip()
        if folder_id:
            qs = qs.filter(folder_id=folder_id)

        q = (self.request.query_params.get("q") or "").strip()
        name = (self.request.query_params.get("name") or "").strip()
        term = q or name

        if term:
            qs = qs.filter(original_name__icontains=term)

        return qs

    @extend_schema(
        summary="Pré-visualizar um arquivo como PDF (com conversão)",
        description=(
            "Retorna um PDF para pré-visualização.\n\n"
            "- Se o arquivo já for PDF: retorna o próprio PDF\n"
            "- Se for DOC/DOCX/PPT/PPTX/XLS/XLSX: converte via LibreOffice e retorna o PDF\n\n"
            "Acesso protegido: somente o dono do arquivo pode visualizar."
        ),
        responses={
            200: OpenApiResponse(description="PDF retornado com sucesso."),
            400: OpenApiResponse(description="Arquivo não suportado para preview."),
            401: OpenApiResponse(description="Não autenticado."),
            404: OpenApiResponse(description="Arquivo não encontrado (ou não pertence ao usuário)."),
            500: OpenApiResponse(description="Falha ao converter para PDF."),
        },
    )
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
            resp["Content-Disposition"] = (
                f'inline; filename="{_safe_filename(obj.original_name or "preview.pdf")}"'
            )
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

    @extend_schema(
        summary="Baixar um arquivo de RELATÓRIO (download protegido)",
        description=(
            "Faz o download do arquivo como attachment. "
            "Acesso protegido: apenas o usuário dono do arquivo (dono da pasta) pode baixar."
        ),
        responses={
            200: OpenApiResponse(description="Arquivo retornado com sucesso."),
            401: OpenApiResponse(description="Não autenticado."),
            404: OpenApiResponse(description="Arquivo não encontrado (ou não pertence ao usuário)."),
        },
    )
    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        obj = self.get_object()

        if not obj.file:
            return Response({"detail": "Arquivo não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        filename = obj.original_name or obj.file.name.split("/")[-1]
        return FileResponse(obj.file.open("rb"), as_attachment=True, filename=filename)


@extend_schema_view(
    destroy=extend_schema(
        summary="Excluir um arquivo de uma pasta de RELATÓRIO",
        description=(
            "Remove um arquivo específico pertencente ao usuário autenticado. "
            "Se configurado, o arquivo físico também é removido do storage."
        ),
        responses={
            204: OpenApiResponse(description="Arquivo excluído com sucesso."),
            401: OpenApiResponse(description="Não autenticado."),
            404: OpenApiResponse(description="Arquivo não encontrado (ou não pertence ao usuário)."),
        },
    )
)
class ReportFileDeleteViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def destroy(self, request, pk=None):
        try:
            obj = ReportFile.objects.get(id=pk, folder__owner=request.user)
        except ReportFile.DoesNotExist:
            return Response({"detail": "Arquivo não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
