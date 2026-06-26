"""Ponto de entrada ASGI (suporte assincrono)."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # Aponta para as configuracoes
application = get_asgi_application()                                 # Aplicacao assincrona que o servidor executa
