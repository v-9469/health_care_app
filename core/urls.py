"""
Master URL Configuration for healthcare project.
"""
from django.contrib import admin
from django.urls import path, include
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

    # Application APIs
    path('api/auth/', include('apps.accounts.urls')),
    path('api/doctors/', include('apps.doctors.urls')),
    path('api/patients/', include('apps.patients.urls')),
    path('api/mappings/', include('apps.mappings.urls')),
]
