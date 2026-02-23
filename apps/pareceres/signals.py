from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ParecerFile


@receiver(post_delete, sender=ParecerFile)
def delete_file_from_storage(sender, instance: ParecerFile, **kwargs):
    if instance.file:
        instance.file.delete(save=False)