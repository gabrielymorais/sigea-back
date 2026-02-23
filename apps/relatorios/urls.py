from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import ReportFolderViewSet, ReportFileViewSet, ReportFileDeleteViewSet

router = DefaultRouter()
router.register(r"relatorios/folders", ReportFolderViewSet, basename="relatorio-folder")
router.register(r"relatorios/files", ReportFileViewSet, basename="relatorio-file")
router.register(r"relatorios/files-delete", ReportFileDeleteViewSet, basename="relatorio-file-delete")

urlpatterns = [
    path("", include(router.urls)),
]