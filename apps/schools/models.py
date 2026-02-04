from django.db import models


class School(models.Model):
    inep = models.CharField("INEP", max_length=20, unique=True)

    nome_gestor = models.CharField("Nome do gestor", max_length=150)

    parecer_regulamentacao = models.CharField(
        "Parecer de regulamentação", max_length=120
    )

    validade_regulamentacao = models.DateField(
        "Validade da regulamentação"
    )

    bairro = models.CharField(max_length=120)
    rua = models.CharField(max_length=180)
    numero = models.CharField(max_length=30)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.inep} - {self.rua}, {self.numero} ({self.bairro})"
