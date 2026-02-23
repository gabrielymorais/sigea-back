from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import OficioFile


@receiver(post_delete, sender=OficioFile)
def delete_file_from_storage(sender, instance: OficioFile, **kwargs):
    if instance.file:
        instance.file.delete(save=False)