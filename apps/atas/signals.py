from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import AtaFile


@receiver(post_delete, sender=AtaFile)
def delete_file_from_storage(sender, instance: AtaFile, **kwargs):
    if instance.file:
        instance.file.delete(save=False)
