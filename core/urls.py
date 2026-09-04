"""
Master URL Configuration for healthcare project (Phase 0: Core Setup).
"""
from django.contrib import admin
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # OpenAPI 3 Schema & Interactive Swagger UI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Feature app routes will be mounted in their respective phases:
    # Phase 1: path('api/auth/', include('apps.accounts.urls'))
    # Phase 2: path('api/patients/', include('apps.patients.urls'))
    # Phase 3: path('api/doctors/', include('apps.doctors.urls'))
    # Phase 4: path('api/mappings/', include('apps.mappings.urls'))
]
