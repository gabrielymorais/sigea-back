from rest_framework.routers import DefaultRouter

from .views import HistoricoAcaoViewSet

router = DefaultRouter()
router.register("historico", HistoricoAcaoViewSet, basename="historico")

urlpatterns = router.urls
