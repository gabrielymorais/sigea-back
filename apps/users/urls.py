from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UsersViewSet, RegisterView, MeView

router = DefaultRouter()
router.register(r"usuarios", UsersViewSet, basename="usuarios")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("auth/", include(router.urls)),
]