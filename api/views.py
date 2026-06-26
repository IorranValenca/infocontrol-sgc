"""Endpoints REST de clientes, produtos, vendas e relatorios.

As views ficam enxutas: recebem a requisicao, chamam a camada de servico
(services.py) quando ha regra de negocio e devolvem JSON.
"""
from rest_framework import viewsets, mixins, status                 # Bases de views e codigos HTTP
from rest_framework.decorators import api_view, permission_classes, action  # Criam endpoints/funcoes extras
from rest_framework.permissions import IsAuthenticated              # Exige login
from rest_framework.response import Response                        # Resposta JSON
from django.db.models import F                                      # Compara dois campos no banco (estoque <= minimo)
from .models import Cliente, Produto, Venda                         # Modelos consultados
from .serializers import ClienteSerializer, ProdutoSerializer, VendaSerializer, VendaCriacaoSerializer
from .services import VendaService, RelatorioService               # Regras de negocio
from .exceptions import RegraNegocioException                       # Erro de negocio (vira HTTP 400)
from .auth import IsAdminPerfil                                     # Permissao de exclusao (somente ADMIN)


class AdminDeleteMixin:
    """Exige perfil ADMIN para excluir (DELETE); as demais acoes pedem apenas login."""

    def get_permissions(self):
        """Escolhe a permissao conforme a acao em andamento."""
        # 'destroy' e a acao de DELETE; nela exige ADMIN, nas outras basta estar logado.
        return [IsAdminPerfil()] if self.action == "destroy" else [IsAuthenticated()]


class ClienteViewSet(AdminDeleteMixin, viewsets.ModelViewSet):
    """CRUD de clientes (GET, POST, PUT, PATCH, DELETE em /api/clientes/)."""

    queryset = Cliente.objects.all().order_by("id")     # Fonte de dados, ordenada por id
    serializer_class = ClienteSerializer                # Serializer usado na conversao JSON

    def destroy(self, request, *args, **kwargs):
        """Bloqueia a exclusao de cliente que possui vendas registradas."""
        if self.get_object().vendas.exists():           # Tem alguma venda ligada a este cliente?
            raise RegraNegocioException("Cliente possui vendas e nao pode ser removido.")
        return super().destroy(request, *args, **kwargs)  # Caso contrario, exclui normalmente


class ProdutoViewSet(AdminDeleteMixin, viewsets.ModelViewSet):
    """CRUD de produtos, mais a consulta de itens com estoque baixo."""

    queryset = Produto.objects.all().order_by("id")
    serializer_class = ProdutoSerializer

    def get_permissions(self):
        """Funcionarios podem ler produtos para vender; alteracoes ficam com ADMIN."""
        return [IsAuthenticated()] if self.action in ("list", "retrieve") else [IsAdminPerfil()]

    def destroy(self, request, *args, **kwargs):
        """Bloqueia a exclusao de produto ja vinculado a alguma venda."""
        if self.get_object().itens_venda.exists():      # Produto aparece em algum item de venda?
            raise RegraNegocioException("Produto esta vinculado a vendas e nao pode ser removido.")
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="estoque-baixo")  # Rota extra: /api/produtos/estoque-baixo/
    def estoque_baixo(self, request):
        """GET /api/produtos/estoque-baixo/ -> produtos no/abaixo do estoque minimo."""
        # F("estoque_minimo") compara o estoque atual com o minimo, campo a campo.
        produtos = Produto.objects.filter(quantidade_estoque__lte=F("estoque_minimo")).order_by("id")
        return Response(ProdutoSerializer(produtos, many=True).data)


class VendaViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Vendas: registrar (POST), listar (GET) e detalhar (GET /{id}/). Nao ha edicao/exclusao."""

    queryset = Venda.objects.all().order_by("-data_venda")  # Mais recentes primeiro
    serializer_class = VendaSerializer
    permission_classes = [IsAuthenticated]                  # Qualquer usuario logado pode vender

    def create(self, request, *args, **kwargs):
        """Valida o corpo e delega o registro da venda para o VendaService."""
        dados = VendaCriacaoSerializer(data=request.data)   # Valida cliente_id + itens
        dados.is_valid(raise_exception=True)                # Erro de validacao vira HTTP 400 automaticamente
        venda = VendaService.registrar_venda(               # Regra de negocio fica no servico
            cliente_id=dados.validated_data["cliente_id"],
            itens=dados.validated_data["itens"],
            usuario=request.user,                           # Funcionario logado = responsavel pela venda
        )
        # Retorna a venda criada com status 201 (criado).
        return Response(VendaSerializer(venda).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAdminPerfil])
def relatorio_periodo(request):
    """GET /api/relatorios/vendas/?inicio=&fim= -> vendas e total de um periodo."""
    vendas, total = RelatorioService.vendas_por_periodo(    # Busca as vendas entre as datas
        request.query_params.get("inicio"), request.query_params.get("fim"))
    return Response({
        "total_vendido": float(total),                      # Soma do periodo
        "quantidade_vendas": vendas.count(),                # Quantas vendas
        "vendas": VendaSerializer(vendas, many=True).data,  # Detalhe de cada venda
    })


@api_view(["GET"])
@permission_classes([IsAdminPerfil])
def relatorio_cliente(request, cliente_id):
    """GET /api/relatorios/vendas-cliente/{id}/ -> historico de compras de um cliente."""
    cliente, vendas, total = RelatorioService.vendas_por_cliente(cliente_id)
    return Response({
        "cliente": cliente.nome,
        "total_vendido": float(total),
        "quantidade_vendas": vendas.count(),
        "vendas": VendaSerializer(vendas, many=True).data,
    })


@api_view(["GET"])
@permission_classes([IsAdminPerfil])
def relatorio_anual(request):
    """GET /api/relatorios/vendas-anuais/?ano= -> total vendido mes a mes (grafico)."""
    ano = int(request.query_params.get("ano", 2026))        # Ano pedido (padrao 2026)
    return Response({"ano": ano, "dados": RelatorioService.vendas_anuais(ano)})


@api_view(["GET"])
@permission_classes([IsAdminPerfil])
def relatorio_mais_vendidos(request):
    """GET /api/relatorios/mais-vendidos/ -> produtos campeoes de venda (best-sellers)."""
    return Response({"produtos": RelatorioService.produtos_mais_vendidos()})
