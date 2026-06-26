"""Camada de servico: concentra as regras de negocio de vendas e relatorios.

Manter essas regras fora das views deixa o codigo organizado, reutilizavel e testavel.
"""
from decimal import Decimal                         # Numeros exatos para dinheiro
from django.db import transaction                   # Permite executar tudo "ou nada" (atomico)
from django.db.models import Sum                    # Soma valores diretamente no banco
from .models import Cliente, Produto, Venda, ItemVenda
from .exceptions import RegraNegocioException       # Erro de negocio (vira HTTP 400)


class VendaService:
    """Regras para registrar uma venda de forma consistente."""

    @staticmethod
    @transaction.atomic  # Tudo ou nada: se algo falhar no meio, nenhuma alteracao e gravada.
    def registrar_venda(cliente_id, itens, usuario):
        """Cria a venda, baixa o estoque de cada item e devolve a venda com o total calculado."""
        cliente = Cliente.objects.filter(id=cliente_id).first()     # Procura o cliente
        if not cliente:
            raise RegraNegocioException("Cliente nao encontrado.")
        if not itens:
            raise RegraNegocioException("Nao e permitido registrar venda sem itens.")

        # Cria a venda com total zero; o valor sera somado item a item abaixo.
        venda = Venda.objects.create(cliente=cliente, usuario=usuario, valor_total=Decimal("0"))
        total = Decimal("0")

        for item in itens:                                          # Para cada item enviado...
            quantidade = int(item.get("quantidade", 0))             # Quantidade pedida
            # select_for_update trava a linha do produto ate o fim da transacao (evita venda dupla do mesmo estoque).
            produto = Produto.objects.select_for_update().filter(id=item.get("produto_id")).first()

            if not produto:
                raise RegraNegocioException(f"Produto {item.get('produto_id')} nao encontrado.")
            if quantidade <= 0:
                raise RegraNegocioException("Quantidade deve ser maior que zero.")
            if produto.quantidade_estoque < quantidade:             # Regra: nao vende sem estoque
                raise RegraNegocioException(f"Estoque insuficiente para {produto.nome}.")

            subtotal = produto.preco * quantidade                   # Subtotal do item
            ItemVenda.objects.create(                               # Grava o item da venda
                venda=venda, produto=produto, quantidade=quantidade,
                preco_unitario=produto.preco, subtotal=subtotal,
            )
            produto.quantidade_estoque -= quantidade                # Atualiza o estoque apos a venda
            produto.save()
            total += subtotal                                       # Acumula no total da venda

        venda.valor_total = total                                   # Valor total calculado automaticamente
        venda.save()
        return venda


class RelatorioService:
    """Consultas agregadas usadas pelos relatorios."""

    @staticmethod
    def vendas_por_periodo(inicio=None, fim=None):
        """Retorna as vendas (e o total) entre duas datas (formato YYYY-MM-DD)."""
        vendas = Venda.objects.all().order_by("-data_venda")
        if inicio:                                                  # Filtra pela data inicial, se informada
            vendas = vendas.filter(data_venda__date__gte=inicio)
        if fim:                                                     # Filtra pela data final, se informada
            vendas = vendas.filter(data_venda__date__lte=fim)
        total = vendas.aggregate(t=Sum("valor_total"))["t"] or Decimal("0")  # Soma (0 se vazio)
        return vendas, total

    @staticmethod
    def vendas_por_cliente(cliente_id):
        """Retorna o cliente, suas vendas e o total comprado por ele."""
        cliente = Cliente.objects.filter(id=cliente_id).first()
        if not cliente:
            raise RegraNegocioException("Cliente nao encontrado.")
        vendas = cliente.vendas.order_by("-data_venda")            # Vendas ligadas a este cliente
        total = vendas.aggregate(t=Sum("valor_total"))["t"] or Decimal("0")
        return cliente, vendas, total

    @staticmethod
    def vendas_anuais(ano):
        """Soma o total vendido em cada mes do ano (base para o grafico anual)."""
        meses = []
        for mes in range(1, 13):                                   # Do mes 1 (Jan) ao 12 (Dez)
            total = Venda.objects.filter(data_venda__year=ano, data_venda__month=mes) \
                .aggregate(t=Sum("valor_total"))["t"] or Decimal("0")
            meses.append({"mes": mes, "total": float(total)})      # Um registro por mes
        return meses

    @staticmethod
    def produtos_mais_vendidos(limite=5):
        """Lista os produtos campeoes de venda (quantidade e receita), do maior para o menor."""
        # Agrupa os itens de venda por produto e soma quantidade e receita.
        dados = (
            ItemVenda.objects.values("produto__nome", "produto__marca")
            .annotate(quantidade=Sum("quantidade"), receita=Sum("subtotal"))
            .order_by("-quantidade")[:limite]
        )
        return [
            {"produto": d["produto__nome"], "marca": d["produto__marca"] or "-",
             "quantidade": d["quantidade"], "receita": float(d["receita"])}
            for d in dados
        ]
