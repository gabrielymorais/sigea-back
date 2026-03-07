from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status, viewsets, filters
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiParameter

from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer

User = get_user_model()


class IsAdminOrSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user and (request.user.is_staff or obj.pk == request.user.pk))


@extend_schema(
    tags=["Auth"],
    summary="Cadastro de usuário",
    request=UserCreateSerializer,
    responses={201: UserSerializer, 400: OpenApiResponse(description="Dados inválidos.")},
    examples=[
        OpenApiExample(
            "Exemplo de cadastro",
            value={
                "username": "gabriely",
                "full_name": "Gabriely Souza Lima",
                "email": "gabriely@email.com",
                "cpf": "123.456.789-00",
                "telefone": "(88) 99999-9999",
                "tipo_profissional": "Professor",
                "escola_lotacao": "IFCE Boa Viagem",
                "portaria": "Portaria 012/2026",
                "password": "12345678",
            },
            request_only=True,
        )
    ],
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        tags=["Auth"],
        summary="Usuário logado",
        description="Retorna os dados do usuário autenticado.",
        responses={200: UserSerializer, 401: OpenApiResponse(description="Não autenticado.")},
    ),
    patch=extend_schema(
        tags=["Auth"],
        summary="Atualizar meu perfil (inclui troca de senha)",
        description=(
            "Atualiza dados do usuário logado. Para trocar senha, enviar "
            "`current_password` e `new_password`."
        ),
        request=UserUpdateSerializer,
        responses={200: UserSerializer, 400: OpenApiResponse(description="Dados inválidos.")},
    ),
)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        tags=["Usuários"],
        summary="Listar usuários",
        parameters=[
            OpenApiParameter(
                name="arquivados",
                required=False,
                type=bool,
                description="Se true, lista apenas usuários arquivados. Se false/ausente, lista ativos.",
            ),
            OpenApiParameter(name="search", required=False, type=str, description="Busca textual (username, nome, email, cpf)."),
            OpenApiParameter(name="ordering", required=False, type=str, description="Ordenação (ex: username, -username)."),
            OpenApiParameter(name="limit", required=False, type=int, description="Paginação (LimitOffsetPagination)."),
            OpenApiParameter(name="offset", required=False, type=int, description="Paginação (LimitOffsetPagination)."),
        ],
    ),
    retrieve=extend_schema(tags=["Usuários"], summary="Detalhar usuário"),
    create=extend_schema(tags=["Usuários"], summary="Criar usuário"),
    partial_update=extend_schema(tags=["Usuários"], summary="Atualizar usuário (parcial)"),
    update=extend_schema(tags=["Usuários"], summary="Atualizar usuário (total)"),
    destroy=extend_schema(tags=["Usuários"], summary="Arquivar usuário (soft delete)"),
)
class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "full_name", "email", "cpf"]
    ordering_fields = ["id", "username", "full_name", "email", "cpf"]
    ordering = ["username"]

    def get_permissions(self):
        if self.action in ["list", "create", "destroy", "desarquivar"]:
            return [IsAuthenticated(), IsAdminUser()]

        if self.action in ["retrieve", "update", "partial_update"]:
            return [IsAuthenticated(), IsAdminOrSelf()]

        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action == "list":
            raw = str(self.request.query_params.get("arquivados", "")).lower()
            wants_archived = raw in ["1", "true", "t", "yes", "sim"]

            qs = qs.filter(is_archived=True) if wants_archived else qs.filter(is_archived=False)

        return qs

    def perform_destroy(self, instance):
        if not instance.is_archived:
            instance.is_archived = True
            instance.archived_at = timezone.now()
            instance.is_active = False
            instance.save(update_fields=["is_archived", "archived_at", "is_active"])

    @action(detail=True, methods=["post"], url_path="desarquivar")
    def desarquivar(self, request, pk=None):
        user = self.get_object()
        user.is_archived = False
        user.archived_at = None
        user.is_active = True
        user.save(update_fields=["is_archived", "archived_at", "is_active"])
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)