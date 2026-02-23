from django.conf import settings
from django.db import models


class OficioFolder(models.Model):
    name = models.CharField(max_length=120)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="oficio_folders",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["name"]), models.Index(fields=["owner"])]

    def __str__(self) -> str:
        return f"{self.name} ({self.owner_id})"


def oficio_file_path(instance: "OficioFile", filename: str) -> str:
    return f"oficios/{instance.folder.owner_id}/folder_{instance.folder_id}/{filename}"


class OficioFile(models.Model):
    folder = models.ForeignKey(OficioFolder, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to=oficio_file_path)
    original_name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def save(self, *args, **kwargs):
        if self.file and not self.original_name:
            self.original_name = self.file.name
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.original_name or str(self.file)