from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),

    path("admin/", admin.site.urls),

    path("api/auth/", include("apps.users.urls")),

    path("api/", include("apps.core.urls")),
    path("api/", include("apps.documents.urls")),
    path("api/", include("apps.schools.urls")),
    path("api/", include("apps.atas.urls")),
    path("api/", include("apps.relatorios.urls")),
    path("api/", include("apps.pareceres.urls")),
    path("api/", include("apps.oficios.urls")),
    path("api/", include("apps.rea.urls")),
    path("api/", include("apps.historico.urls")),


    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
