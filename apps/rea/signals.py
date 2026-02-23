from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ReaFile


@receiver(post_delete, sender=ReaFile)
def delete_file_from_storage(sender, instance: ReaFile, **kwargs):
    if instance.file:
        instance.file.delete(save=False)