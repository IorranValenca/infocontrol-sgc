"""Registro do app 'web' (interface grafica que consome a API REST)."""
from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # Tipo padrao das chaves primarias (id)
    name = "web"                                          # Nome do app
