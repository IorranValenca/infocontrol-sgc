from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class PerfilUsuario(models.Model):
    PERFIS = (
        ('ADMIN', 'Administrador'),
        ('FUNCIONARIO', 'Funcionário'),
    )

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_usuario')
    perfil = models.CharField(max_length=20, choices=PERFIS, default='FUNCIONARIO')

    def __str__(self):
        return f'{self.usuario.username} - {self.perfil}'


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    quantidade_estoque = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    estoque_minimo = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.nome

    @property
    def estoque_baixo(self):
        return self.quantidade_estoque <= self.estoque_minimo


class Venda(models.Model):
    data_venda = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='vendas')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='vendas')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'Venda #{self.id} - {self.cliente.nome}'


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.IntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome}'
