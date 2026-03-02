from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Campos do cadastro (todos obrigatórios)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)

    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20)

    tipo_profissional = models.CharField(max_length=60)
    escola_lotacao = models.CharField(max_length=120)
    portaria = models.CharField(max_length=60)

    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    REQUIRED_FIELDS = [
        "email",
        "full_name",
        "cpf",
        "telefone",
        "tipo_profissional",
        "escola_lotacao",
        "portaria",
    ]

    def __str__(self):
        return f"{self.username} - {self.full_name}"