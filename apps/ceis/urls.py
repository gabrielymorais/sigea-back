from rest_framework.routers import DefaultRouter
from ceis.views import CEIViewSet  # ajuste o import

router = DefaultRouter()
router.register(r"ceis", CEIViewSet, basename="ceis")

urlpatterns = [
    path("", include(router.urls)),
]