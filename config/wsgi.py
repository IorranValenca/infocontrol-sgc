"""Ponto de entrada WSGI usado por servidores de producao (gunicorn, etc.)."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # Aponta para as configuracoes
application = get_wsgi_application()                                 # Aplicacao que o servidor executa
