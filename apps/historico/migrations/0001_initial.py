from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricoAcao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="historico_acoes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "acao",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("CRIAR", "Criar"),
                            ("EDITAR", "Editar"),
                            ("EXCLUIR", "Excluir"),
                            ("UPLOAD", "Upload"),
                            ("DOWNLOAD", "Download"),
                            ("VISUALIZAR", "Visualizar"),
                        ],
                    ),
                ),
                (
                    "modulo",
                    models.CharField(
                        default="OUTRO",
                        max_length=20,
                        choices=[
                            ("ATAS", "Atas"),
                            ("DOCUMENTOS", "Documentos"),
                            ("RELATORIOS", "Relatórios"),
                            ("PARECERES", "Pareceres"),
                            ("OFICIOS", "Ofícios"),
                            ("REA", "REA"),
                            ("USUARIOS", "Usuários"),
                            ("OUTRO", "Outro"),
                        ],
                    ),
                ),
                ("descricao", models.CharField(max_length=500)),
                ("objeto_id", models.PositiveIntegerField(blank=True, null=True)),
                ("objeto_nome", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="historicoacao",
            index=models.Index(fields=["usuario"], name="historico_usuario_idx"),
        ),
        migrations.AddIndex(
            model_name="historicoacao",
            index=models.Index(fields=["created_at"], name="historico_created_idx"),
        ),
        migrations.AddIndex(
            model_name="historicoacao",
            index=models.Index(fields=["modulo"], name="historico_modulo_idx"),
        ),
    ]
