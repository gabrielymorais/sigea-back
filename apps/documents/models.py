from django.conf import settings
from django.db import models


class DocumentType(models.TextChoices):
    OFICIO = "OFICIO", "Ofício"
    ATA = "ATA", "Ata"
    RELATORIO = "RELATORIO", "Relatório"
    REA = "REA", "REA"
    ESCOLA = "ESCOLA", "Escola"


def document_upload_to(instance, filename: str) -> str:
    # organiza por usuário para evitar caos no storage
    return f"documents/user_{instance.owner_id}/{filename}"


class Document(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    name = models.CharField(max_length=180)
    doc_type = models.CharField(max_length=20, choices=DocumentType.choices)
    file = models.FileField(upload_to=document_upload_to)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.doc_type})"
