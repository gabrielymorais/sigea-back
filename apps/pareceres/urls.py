from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import ParecerFolderViewSet, ParecerFileViewSet, ParecerFileDeleteViewSet

router = DefaultRouter()
router.register(r"pareceres/folders", ParecerFolderViewSet, basename="parecer-folder")
router.register(r"pareceres/files", ParecerFileViewSet, basename="parecer-file")
router.register(r"pareceres/files-delete", ParecerFileDeleteViewSet, basename="parecer-file-delete")

urlpatterns = [
    path("", include(router.urls)),
]