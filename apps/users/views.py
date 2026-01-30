from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from .serializers import RegisterSerializer, UserSerializer


@extend_schema(
    tags=["Auth"],
    summary="Cadastro de usuário",
    description="Cria um novo usuário com username, email, senha, matrícula e nome da escola.",
    request=RegisterSerializer,
    responses={
        201: UserSerializer,
        400: OpenApiResponse(description="Dados inválidos (validação do serializer)."),
    },
    examples=[
        OpenApiExample(
            "Exemplo de cadastro",
            value={
                "username": "gabriely",
                "email": "gabriely@email.com",
                "password": "12345678",
                "matricula": "20260001",
                "schoolName": "IFCE Boa Viagem",
            },
            request_only=True,
        )
    ],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Auth"],
    summary="Usuário logado",
    description="Retorna os dados do usuário autenticado (Bearer token).",
    responses={
        200: UserSerializer,
        401: OpenApiResponse(description="Não autenticado (token ausente/inválido)."),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
