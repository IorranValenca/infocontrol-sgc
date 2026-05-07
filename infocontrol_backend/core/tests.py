from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Cliente, Produto

class InfoControlAPITest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='123456')
        self.client_api = APIClient()

        login = self.client_api.post('/api/auth/login/', {
            'username': 'admin',
            'password': '123456'
        }, format='json')

        token = login.data['access']
        self.client_api.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        self.cliente = Cliente.objects.create(
            nome='João Silva',
            cpf='12345678901',
            email='joao@email.com',
            telefone='61999999999',
            endereco='Brasília'
        )

        self.produto = Produto.objects.create(
            nome='Mouse Gamer',
            descricao='Mouse USB',
            preco=100.00,
            quantidade_estoque=10,
            estoque_minimo=2
        )

    def test_criar_cliente(self):
        response = self.client_api.post('/api/clientes/', {
            'nome': 'Maria Souza',
            'cpf': '98765432100',
            'email': 'maria@email.com',
            'telefone': '61988888888',
            'endereco': 'Brasília'
        }, format='json')

        self.assertEqual(response.status_code, 201)

    def test_criar_produto(self):
        response = self.client_api.post('/api/produtos/', {
            'nome': 'Teclado Mecânico',
            'descricao': 'Teclado RGB',
            'preco': '250.00',
            'quantidade_estoque': 5,
            'estoque_minimo': 1
        }, format='json')

        self.assertEqual(response.status_code, 201)

    def test_registrar_venda_baixa_estoque(self):
        response = self.client_api.post('/api/vendas/', {
            'cliente_id': self.cliente.id,
            'itens': [
                {
                    'produto_id': self.produto.id,
                    'quantidade': 2
                }
            ]
        }, format='json')

        self.assertEqual(response.status_code, 201)

        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade_estoque, 8)

    def test_estoque_insuficiente(self):
        response = self.client_api.post('/api/vendas/', {
            'cliente_id': self.cliente.id,
            'itens': [
                {
                    'produto_id': self.produto.id,
                    'quantidade': 99
                }
            ]
        }, format='json')

        self.assertEqual(response.status_code, 400)
