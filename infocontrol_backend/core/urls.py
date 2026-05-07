from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClienteViewSet,
    ProdutoViewSet,
    VendaViewSet,
    relatorio_vendas_periodo,
    relatorio_vendas_cliente,
    relatorio_vendas_anuais,
)

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'produtos', ProdutoViewSet)
router.register(r'vendas', VendaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('relatorios/vendas/', relatorio_vendas_periodo),
    path('relatorios/vendas-cliente/<int:cliente_id>/', relatorio_vendas_cliente),
    path('relatorios/vendas-anuais/', relatorio_vendas_anuais),
]
