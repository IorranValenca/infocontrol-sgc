"""Modelos do dominio: usuario (perfil), cliente, produto, venda e item de venda.

Cada classe vira uma tabela no banco de dados. Os nomes de tabela (db_table)
seguem o script SQL entregue na modelagem (clientes, produtos, vendas, itens_venda).
"""
from decimal import Decimal                              # Tipo numerico exato para valores em dinheiro
from django.db import models                             # Base para criar modelos/tabelas
from django.contrib.auth.models import User             # Usuario padrao do Django (login e senha)
from django.core.validators import MinValueValidator    # Valida valores minimos (ex.: nao negativo)


class PerfilUsuario(models.Model):
    """Liga um usuario do Django a um perfil de acesso (ADMIN ou FUNCIONARIO)."""

    # Opcoes possiveis de perfil (valor salvo, texto exibido).
    PERFIS = (("ADMIN", "Administrador"), ("FUNCIONARIO", "Funcionario"))

    usuario = models.OneToOneField(            # Cada usuario tem exatamente um perfil
        User, on_delete=models.CASCADE,        # Se o usuario for apagado, o perfil tambem e
        related_name="perfil_usuario",         # Permite acessar usuario.perfil_usuario
    )
    perfil = models.CharField(                 # Texto do perfil
        max_length=20, choices=PERFIS,         # So aceita os valores definidos em PERFIS
        default="FUNCIONARIO",                 # Perfil padrao ao cadastrar
    )

    class Meta:
        db_table = "perfis_usuario"            # Nome real da tabela no banco

    def __str__(self):
        """Texto exibido no admin e em logs."""
        return f"{self.usuario.username} ({self.perfil})"


class Cliente(models.Model):
    """Cliente da loja. O CPF e unico; vendas vinculadas impedem a exclusao."""

    nome = models.CharField(max_length=100)                     # Nome do cliente
    cpf = models.CharField(max_length=14, unique=True)          # CPF (nao pode repetir)
    email = models.EmailField()                                 # E-mail (formato validado pelo Django)
    telefone = models.CharField(max_length=20, blank=True, null=True)    # Telefone (opcional)
    endereco = models.CharField(max_length=150, blank=True, null=True)   # Endereco (opcional)

    class Meta:
        db_table = "clientes"                                   # Nome real da tabela no banco

    def __str__(self):
        """Mostra o nome do cliente."""
        return self.nome


class Produto(models.Model):
    """Produto do catalogo da loja de informatica. Preco e estoque nunca sao negativos."""

    # Categorias tipicas de uma loja de informatica/assistencia tecnica.
    CATEGORIAS = (
        ("NOTEBOOK", "Notebooks"), ("COMPUTADOR", "Computadores"), ("PERIFERICO", "Perifericos"),
        ("COMPONENTE", "Componentes"), ("MONITOR", "Monitores"), ("ARMAZENAMENTO", "Armazenamento"),
        ("REDE", "Redes"), ("ACESSORIO", "Acessorios"), ("OUTROS", "Outros"),
    )

    nome = models.CharField(max_length=100)                     # Nome do produto
    descricao = models.TextField(blank=True, null=True)         # Descricao detalhada (opcional)
    marca = models.CharField(max_length=50, blank=True, null=True)   # Fabricante (Dell, Logitech, AMD, Intel...)
    categoria = models.CharField(                               # Categoria no catalogo
        max_length=20, choices=CATEGORIAS, default="OUTROS",
    )
    preco = models.DecimalField(                                # Preco de venda
        max_digits=10, decimal_places=2,                        # Ate 99.999.999,99
        validators=[MinValueValidator(Decimal("0"))],           # Nao pode ser negativo
    )
    quantidade_estoque = models.IntegerField(                   # Quantidade disponivel em estoque
        default=0, validators=[MinValueValidator(0)],           # Comeca em 0 e nao fica negativo
    )
    estoque_minimo = models.IntegerField(                       # Limite para alertar reposicao
        default=0, validators=[MinValueValidator(0)],
    )
    garantia_meses = models.IntegerField(                       # Garantia do produto, em meses (tipico em tech)
        default=12, validators=[MinValueValidator(0)],
    )

    class Meta:
        db_table = "produtos"                                   # Nome real da tabela no banco

    def __str__(self):
        """Mostra o nome do produto."""
        return self.nome

    @property
    def estoque_baixo(self):
        """True quando o estoque atingiu (ou ficou abaixo de) o minimo configurado."""
        return self.quantidade_estoque <= self.estoque_minimo


class Venda(models.Model):
    """Venda registrada. O valor_total e calculado a partir dos itens."""

    data_venda = models.DateTimeField(auto_now_add=True)        # Data/hora gravada automaticamente
    cliente = models.ForeignKey(                                # Cliente que comprou
        Cliente, on_delete=models.PROTECT,                      # PROTECT: nao deixa apagar cliente com venda
        related_name="vendas",                                  # Permite acessar cliente.vendas
    )
    usuario = models.ForeignKey(                                # Funcionario que registrou a venda
        User, on_delete=models.PROTECT, related_name="vendas",
    )
    valor_total = models.DecimalField(                          # Soma dos subtotais dos itens
        max_digits=10, decimal_places=2, default=0,
    )

    class Meta:
        db_table = "vendas"                                     # Nome real da tabela no banco

    def __str__(self):
        """Identifica a venda pelo numero e cliente."""
        return f"Venda #{self.id} - {self.cliente.nome}"


class ItemVenda(models.Model):
    """Item de uma venda: produto, quantidade e o subtotal (preco x quantidade)."""

    venda = models.ForeignKey(                                  # Venda a que o item pertence
        Venda, on_delete=models.CASCADE,                        # CASCADE: apagar a venda apaga os itens
        related_name="itens",                                   # Permite acessar venda.itens
    )
    produto = models.ForeignKey(                                # Produto vendido neste item
        Produto, on_delete=models.PROTECT,                      # Nao deixa apagar produto usado em venda
        related_name="itens_venda",
    )
    quantidade = models.IntegerField(validators=[MinValueValidator(1)])    # Quantidade vendida (>= 1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Preco do produto no momento da venda
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)        # preco_unitario x quantidade

    class Meta:
        db_table = "itens_venda"                                # Nome real da tabela no banco

    def __str__(self):
        """Resume o item (quantidade x produto)."""
        return f"{self.quantidade}x {self.produto.nome}"
