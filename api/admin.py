"""Registra os modelos no painel administrativo do Django (/admin/)."""
from django.contrib import admin
from .models import PerfilUsuario, Cliente, Produto, Venda, ItemVenda

admin.site.register([PerfilUsuario, Cliente, Produto, Venda, ItemVenda])
