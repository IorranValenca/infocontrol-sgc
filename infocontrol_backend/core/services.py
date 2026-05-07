from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.utils.dateparse import parse_date
from .models import Cliente, Produto, Venda, ItemVenda
from .exceptions import RegraNegocioException

class VendaService:

    @staticmethod
    @transaction.atomic
    def registrar_venda(cliente_id, itens, usuario):
        try:
            cliente = Cliente.objects.get(id=cliente_id)
        except Cliente.DoesNotExist:
            raise RegraNegocioException('Cliente não encontrado.')

        if not itens:
            raise RegraNegocioException('Não é permitido registrar venda sem itens.')

        venda = Venda.objects.create(cliente=cliente, usuario=usuario, valor_total=Decimal('0.00'))

        valor_total = Decimal('0.00')

        for item in itens:
            produto_id = item.get('produto_id')
            quantidade = item.get('quantidade')

            try:
                produto = Produto.objects.select_for_update().get(id=produto_id)
            except Produto.DoesNotExist:
                raise RegraNegocioException(f'Produto ID {produto_id} não encontrado.')

            if quantidade <= 0:
                raise RegraNegocioException('Quantidade deve ser maior que zero.')

            if produto.quantidade_estoque < quantidade:
                raise RegraNegocioException(f'Estoque insuficiente para o produto {produto.nome}.')

            preco_unitario = produto.preco
            subtotal = preco_unitario * quantidade

            ItemVenda.objects.create(
                venda=venda,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=preco_unitario,
                subtotal=subtotal
            )

            produto.quantidade_estoque -= quantidade
            produto.save()

            valor_total += subtotal

        venda.valor_total = valor_total
        venda.save()

        return venda


class RelatorioService:

    @staticmethod
    def vendas_por_periodo(inicio=None, fim=None):
        vendas = Venda.objects.all().order_by('-data_venda')

        if inicio:
            vendas = vendas.filter(data_venda__date__gte=inicio)

        if fim:
            vendas = vendas.filter(data_venda__date__lte=fim)

        total = vendas.aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')

        return vendas, total

    @staticmethod
    def vendas_por_cliente(cliente_id):
        try:
            cliente = Cliente.objects.get(id=cliente_id)
        except Cliente.DoesNotExist:
            raise RegraNegocioException('Cliente não encontrado.')

        vendas = Venda.objects.filter(cliente=cliente).order_by('-data_venda')
        total = vendas.aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')

        return cliente, vendas, total

    @staticmethod
    def vendas_anuais(ano):
        meses = []
        for mes in range(1, 13):
            total = Venda.objects.filter(
                data_venda__year=ano,
                data_venda__month=mes
            ).aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')

            meses.append({
                'mes': mes,
                'total': float(total)
            })

        return meses
