from django.conf import settings
from django.db import models


class TipoAcao(models.TextChoices):
    CRIAR = "CRIAR", "Criar"
    EDITAR = "EDITAR", "Editar"
    EXCLUIR = "EXCLUIR", "Excluir"
    UPLOAD = "UPLOAD", "Upload"
    DOWNLOAD = "DOWNLOAD", "Download"
    VISUALIZAR = "VISUALIZAR", "Visualizar"


class Modulo(models.TextChoices):
    ATAS = "ATAS", "Atas"
    DOCUMENTOS = "DOCUMENTOS", "Documentos"
    RELATORIOS = "RELATORIOS", "Relatórios"
    PARECERES = "PARECERES", "Pareceres"
    OFICIOS = "OFICIOS", "Ofícios"
    REA = "REA", "REA"
    USUARIOS = "USUARIOS", "Usuários"
    OUTRO = "OUTRO", "Outro"


class HistoricoAcao(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="historico_acoes",
    )
    acao = models.CharField(max_length=20, choices=TipoAcao.choices)
    modulo = models.CharField(max_length=20, choices=Modulo.choices, default=Modulo.OUTRO)
    descricao = models.CharField(max_length=500)
    objeto_id = models.PositiveIntegerField(null=True, blank=True)
    objeto_nome = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["usuario"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["modulo"]),
        ]

    def __str__(self) -> str:
        return f"{self.usuario_id} | {self.acao} | {self.modulo} | {self.created_at:%d/%m/%Y %H:%M}"
