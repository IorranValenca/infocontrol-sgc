"""Rotas da API REST (prefixadas por /api/ no config/urls.py)."""
from django.urls import path, include                          # Define caminhos e inclui outros conjuntos de rotas
from rest_framework.routers import DefaultRouter               # Cria automaticamente as rotas dos ViewSets
from rest_framework_simplejwt.views import TokenRefreshView    # Endpoint pronto para renovar o token
from . import views, auth                                      # Nossas views da API e de autenticacao

# O router gera automaticamente as rotas REST (GET/POST/PUT/DELETE) de cada ViewSet.
router = DefaultRouter()
router.register("clientes", views.ClienteViewSet)              # Cria /clientes/ e /clientes/{id}/
router.register("produtos", views.ProdutoViewSet)              # Cria /produtos/ e /produtos/{id}/
router.register("vendas", views.VendaViewSet)                  # Cria /vendas/ e /vendas/{id}/

urlpatterns = [
    # Autenticacao e recuperacao de senha
    path("auth/login/", auth.LoginView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("auth/me/", auth.usuario_logado),
    path("auth/recuperar-senha/", auth.recuperar_senha),
    path("auth/redefinir-senha/", auth.redefinir_senha),

    # Relatorios
    path("relatorios/vendas/", views.relatorio_periodo),
    path("relatorios/vendas-cliente/<int:cliente_id>/", views.relatorio_cliente),
    path("relatorios/vendas-anuais/", views.relatorio_anual),
    path("relatorios/mais-vendidos/", views.relatorio_mais_vendidos),

    # CRUD de clientes, produtos e vendas
    path("", include(router.urls)),
]
