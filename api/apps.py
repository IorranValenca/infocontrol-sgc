"""Registro do app 'api' (camada de negocio e endpoints REST)."""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # Tipo padrao das chaves primarias (id)
    name = "api"                                          # Nome do app
