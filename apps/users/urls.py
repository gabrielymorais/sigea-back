from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import register, me, UsersViewSet

router = DefaultRouter()
router.register(r"usuarios", UsersViewSet, basename="usuarios")

urlpatterns = [
    path("register/", register),
    path("login/", TokenObtainPairView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("me/", me),

    path("", include(router.urls)),
]