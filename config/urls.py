"""Roteamento principal: admin, interface web e API REST."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),   # Painel administrativo do Django
    path("api/", include("api.urls")),  # Endpoints REST (JSON)
    path("", include("web.urls")),      # Interface web (telas HTML)
]
