from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Cliente, Produto, Venda, ItemVenda, PerfilUsuario

class UsuarioSerializer(serializers.ModelSerializer):
    perfil = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'perfil']

    def get_perfil(self, obj):
        if hasattr(obj, 'perfil_usuario'):
            return obj.perfil_usuario.perfil
        return None


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

    def validate_cpf(self, value):
        if len(value) < 11:
            raise serializers.ValidationError('CPF inválido.')
        return value


class ProdutoSerializer(serializers.ModelSerializer):
    estoque_baixo = serializers.ReadOnlyField()

    class Meta:
        model = Produto
        fields = '__all__'

    def validate_preco(self, value):
        if value < 0:
            raise serializers.ValidationError('Preço não pode ser negativo.')
        return value


class ItemVendaLeituraSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)

    class Meta:
        model = ItemVenda
        fields = ['id', 'produto', 'produto_nome', 'quantidade', 'preco_unitario', 'subtotal']


class VendaSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    itens = ItemVendaLeituraSerializer(many=True, read_only=True)

    class Meta:
        model = Venda
        fields = ['id', 'data_venda', 'cliente', 'cliente_nome', 'usuario', 'usuario_username', 'valor_total', 'itens']
        read_only_fields = ['usuario', 'valor_total']


class ItemVendaCriacaoSerializer(serializers.Serializer):
    produto_id = serializers.IntegerField()
    quantidade = serializers.IntegerField(min_value=1)


class VendaCriacaoSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    itens = ItemVendaCriacaoSerializer(many=True)

    def validate_itens(self, value):
        if not value:
            raise serializers.ValidationError('A venda precisa ter pelo menos um item.')
        return value
