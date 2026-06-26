"""Rotas da interface web (telas HTML)."""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.login),                  # Tela de login (pagina inicial)
    path("recuperar/", views.recuperar),     # Recuperacao de senha
    path("clientes/", views.clientes),       # Cadastro de clientes
    path("produtos/", views.produtos),       # Cadastro de produtos
    path("vendas/", views.vendas),           # Registro de vendas
    path("relatorios/", views.relatorios),   # Relatorios de vendas
]
