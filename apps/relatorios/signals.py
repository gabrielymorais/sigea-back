from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ReportFile


@receiver(post_delete, sender=ReportFile)
def delete_file_from_storage(sender, instance: ReportFile, **kwargs):
    if instance.file:
        instance.file.delete(save=False)
