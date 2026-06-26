"""Serializers: convertem modelos <-> JSON e validam os dados de entrada.

O DRF usa estas classes para transformar objetos Python em JSON (na resposta)
e para validar o JSON recebido (na requisicao) antes de salvar no banco.
"""
from rest_framework import serializers                          # Ferramentas de serializacao do DRF
from .models import Cliente, Produto, Venda, ItemVenda          # Modelos que serao convertidos


class ClienteSerializer(serializers.ModelSerializer):
    """Entrada/saida de Cliente. A unicidade do CPF e garantida pelo modelo."""

    class Meta:
        model = Cliente             # Modelo de origem
        fields = "__all__"          # Inclui todos os campos do modelo no JSON

    def validate_cpf(self, value):
        """Recusa CPF com menos de 11 digitos (validacao executada antes de salvar)."""
        if len(value) < 11:
            raise serializers.ValidationError("CPF invalido.")
        return value


class ProdutoSerializer(serializers.ModelSerializer):
    """Entrada/saida de Produto, incluindo o indicador calculado 'estoque_baixo'."""

    # Campo somente-leitura vindo da @property estoque_baixo do modelo.
    estoque_baixo = serializers.ReadOnlyField()

    class Meta:
        model = Produto
        fields = "__all__"

    def validate_preco(self, value):
        """Garante que o preco nao seja negativo."""
        if value < 0:
            raise serializers.ValidationError("Preco nao pode ser negativo.")
        return value


class ItemVendaSerializer(serializers.ModelSerializer):
    """Leitura de um item dentro de uma venda (inclui o nome do produto)."""

    # Campo extra: traz o nome do produto sem precisar de outra requisicao.
    produto_nome = serializers.CharField(source="produto.nome", read_only=True)

    class Meta:
        model = ItemVenda
        # Campos expostos no JSON do item.
        fields = ["id", "produto", "produto_nome", "quantidade", "preco_unitario", "subtotal"]


class VendaSerializer(serializers.ModelSerializer):
    """Leitura de uma venda com cliente, usuario responsavel e itens."""

    cliente_nome = serializers.CharField(source="cliente.nome", read_only=True)        # Nome do cliente
    usuario_nome = serializers.CharField(source="usuario.username", read_only=True)    # Quem registrou
    itens = ItemVendaSerializer(many=True, read_only=True)                             # Lista de itens da venda

    class Meta:
        model = Venda
        # Campos expostos no JSON da venda.
        fields = ["id", "data_venda", "cliente", "cliente_nome", "usuario", "usuario_nome", "valor_total", "itens"]


class VendaCriacaoSerializer(serializers.Serializer):
    """Valida o corpo da criacao de venda: um cliente e uma lista de itens.

    Nao herda de ModelSerializer porque o formato de entrada (cliente_id + itens)
    e diferente do modelo Venda; a venda em si e montada no VendaService.
    """

    cliente_id = serializers.IntegerField()                     # Id do cliente da venda
    itens = serializers.ListField(                              # Lista de itens...
        child=serializers.DictField(),                          # ...cada item e um dicionario {produto_id, quantidade}
        allow_empty=False,                                      # Nao permite venda sem itens
    )
