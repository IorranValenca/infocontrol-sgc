from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import ProtectedError
from .models import Cliente, Produto, Venda
from .serializers import ClienteSerializer, ProdutoSerializer, VendaSerializer, VendaCriacaoSerializer
from .services import VendaService, RelatorioService
from .exceptions import RegraNegocioException

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by('id')
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        cliente = self.get_object()

        if cliente.vendas.exists():
            return Response(
                {'erro': 'Cliente não pode ser removido pois possui vendas registradas.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(request, *args, **kwargs)


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all().order_by('id')
    serializer_class = ProdutoSerializer
    permission_classes = [IsAuthenticated]


class VendaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Venda.objects.all().order_by('-data_venda')
    serializer_class = VendaSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = VendaCriacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        venda = VendaService.registrar_venda(
            cliente_id=serializer.validated_data['cliente_id'],
            itens=serializer.validated_data['itens'],
            usuario=request.user
        )

        return Response(VendaSerializer(venda).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def relatorio_vendas_periodo(request):
    inicio = request.query_params.get('inicio')
    fim = request.query_params.get('fim')

    vendas, total = RelatorioService.vendas_por_periodo(inicio=inicio, fim=fim)

    return Response({
        'inicio': inicio,
        'fim': fim,
        'total_vendido': float(total),
        'quantidade_vendas': vendas.count(),
        'vendas': VendaSerializer(vendas, many=True).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def relatorio_vendas_cliente(request, cliente_id):
    cliente, vendas, total = RelatorioService.vendas_por_cliente(cliente_id)

    return Response({
        'cliente': cliente.nome,
        'total_vendido': float(total),
        'quantidade_vendas': vendas.count(),
        'vendas': VendaSerializer(vendas, many=True).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def relatorio_vendas_anuais(request):
    ano = int(request.query_params.get('ano', 2026))
    dados = RelatorioService.vendas_anuais(ano)

    return Response({
        'ano': ano,
        'dados': dados
    })
