from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import AtaFolderViewSet, AtaFileViewSet, AtaFileDeleteViewSet

router = DefaultRouter()
router.register(r"atas/folders", AtaFolderViewSet, basename="ata-folder")
router.register(r"atas/files", AtaFileViewSet, basename="ata-file")
router.register(r"atas/files-delete", AtaFileDeleteViewSet, basename="ata-file-delete")

urlpatterns = [
    path("", include(router.urls)),
]
