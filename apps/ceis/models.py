from django.db import models


class CEI(models.Model):
    # Campos (mesmos da School)
    inep = models.CharField(max_length=32, unique=True)
    nome_gestor = models.CharField(max_length=150)
    parecer_regulamentacao = models.CharField(max_length=120)
    validade_regulamentacao = models.DateField()

    bairro = models.CharField(max_length=120)
    rua = models.CharField(max_length=160)
    numero = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CEI"
        verbose_name_plural = "CEIs"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.inep} - {self.nome_gestor}"