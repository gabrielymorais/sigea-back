from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import OficioFolderViewSet, OficioFileViewSet, OficioFileDeleteViewSet

router = DefaultRouter()
router.register(r"oficios/folders", OficioFolderViewSet, basename="oficio-folder")
router.register(r"oficios/files", OficioFileViewSet, basename="oficio-file")
router.register(r"oficios/files-delete", OficioFileDeleteViewSet, basename="oficio-file-delete")

urlpatterns = [
    path("", include(router.urls)),
]