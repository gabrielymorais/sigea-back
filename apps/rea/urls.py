from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import ReaFolderViewSet, ReaFileViewSet, ReaFileDeleteViewSet

router = DefaultRouter()
router.register(r"rea/folders", ReaFolderViewSet, basename="rea-folder")
router.register(r"rea/files", ReaFileViewSet, basename="rea-file")
router.register(r"rea/files-delete", ReaFileDeleteViewSet, basename="rea-file-delete")

urlpatterns = [
    path("", include(router.urls)),
]