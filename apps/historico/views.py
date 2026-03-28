from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .models import HistoricoAcao
from .serializers import HistoricoAcaoSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Listar histórico de ações do usuário",
        description=(
            "Retorna todas as ações realizadas pelo usuário autenticado, "
            "ordenadas da mais recente para a mais antiga.\n\n"
            "Filtros disponíveis:\n"
            "- `?modulo=ATAS` — filtra por módulo\n"
            "- `?acao=CRIAR` — filtra por tipo de ação\n"
        ),
        parameters=[
            OpenApiParameter(
                name="modulo",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filtra pelo módulo (ex: ATAS, DOCUMENTOS, RELATORIOS, PARECERES, OFICIOS, REA, USUARIOS, OUTRO).",
            ),
            OpenApiParameter(
                name="acao",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filtra pelo tipo de ação (ex: CRIAR, EDITAR, EXCLUIR, UPLOAD, DOWNLOAD, VISUALIZAR).",
            ),
        ],
    ),
)
class HistoricoAcaoViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HistoricoAcaoSerializer

    def get_queryset(self):
        qs = HistoricoAcao.objects.filter(usuario=self.request.user)

        modulo = (self.request.query_params.get("modulo") or "").strip().upper()
        if modulo:
            qs = qs.filter(modulo=modulo)

        acao = (self.request.query_params.get("acao") or "").strip().upper()
        if acao:
            qs = qs.filter(acao=acao)

        return qs
