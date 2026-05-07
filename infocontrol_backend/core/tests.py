from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Cliente, Produto, Venda, ItemVenda


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

    # --- Clientes ---

    def test_criar_cliente(self):
        response = self.client_api.post('/api/clientes/', {
            'nome': 'Maria Souza',
            'cpf': '98765432100',
            'email': 'maria@email.com',
            'telefone': '61988888888',
            'endereco': 'Brasília'
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['nome'], 'Maria Souza')

    def test_listar_clientes(self):
        response = self.client_api.get('/api/clientes/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_atualizar_cliente(self):
        response = self.client_api.patch(f'/api/clientes/{self.cliente.id}/', {
            'telefone': '61911111111'
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['telefone'], '61911111111')

    def test_deletar_cliente_sem_vendas(self):
        cliente_sem_vendas = Cliente.objects.create(
            nome='Temp',
            cpf='00000000001',
            email='temp@email.com'
        )
        response = self.client_api.delete(f'/api/clientes/{cliente_sem_vendas.id}/')
        self.assertEqual(response.status_code, 204)

    def test_deletar_cliente_com_vendas_retorna_erro(self):
        Venda.objects.create(cliente=self.cliente, usuario=self.user, valor_total=100)
        response = self.client_api.delete(f'/api/clientes/{self.cliente.id}/')
        self.assertEqual(response.status_code, 400)

    def test_cpf_invalido_retorna_erro(self):
        response = self.client_api.post('/api/clientes/', {
            'nome': 'Inválido',
            'cpf': '123',
            'email': 'invalido@email.com'
        }, format='json')
        self.assertEqual(response.status_code, 400)

    # --- Produtos ---

    def test_criar_produto(self):
        response = self.client_api.post('/api/produtos/', {
            'nome': 'Teclado Mecânico',
            'descricao': 'Teclado RGB',
            'preco': '250.00',
            'quantidade_estoque': 5,
            'estoque_minimo': 1
        }, format='json')

        self.assertEqual(response.status_code, 201)

    def test_listar_produtos(self):
        response = self.client_api.get('/api/produtos/')
        self.assertEqual(response.status_code, 200)

    def test_atualizar_produto(self):
        response = self.client_api.patch(f'/api/produtos/{self.produto.id}/', {
            'preco': '120.00'
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['preco'], '120.00')

    def test_produto_estoque_baixo(self):
        produto_critico = Produto.objects.create(
            nome='Produto Crítico',
            preco=50.00,
            quantidade_estoque=1,
            estoque_minimo=5
        )
        response = self.client_api.get('/api/produtos/estoque-baixo/')
        self.assertEqual(response.status_code, 200)
        ids = [p['id'] for p in response.data]
        self.assertIn(produto_critico.id, ids)

    def test_preco_negativo_retorna_erro(self):
        response = self.client_api.post('/api/produtos/', {
            'nome': 'Produto Ruim',
            'preco': '-10.00',
            'quantidade_estoque': 5,
            'estoque_minimo': 1
        }, format='json')
        self.assertEqual(response.status_code, 400)

    # --- Vendas ---

    def test_registrar_venda_baixa_estoque(self):
        response = self.client_api.post('/api/vendas/', {
            'cliente_id': self.cliente.id,
            'itens': [
                {'produto_id': self.produto.id, 'quantidade': 2}
            ]
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade_estoque, 8)

    def test_estoque_insuficiente(self):
        response = self.client_api.post('/api/vendas/', {
            'cliente_id': self.cliente.id,
            'itens': [
                {'produto_id': self.produto.id, 'quantidade': 99}
            ]
        }, format='json')

        self.assertEqual(response.status_code, 400)

    def test_venda_valor_total_calculado(self):
        response = self.client_api.post('/api/vendas/', {
            'cliente_id': self.cliente.id,
            'itens': [
                {'produto_id': self.produto.id, 'quantidade': 3}
            ]
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(float(response.data['valor_total']), 300.00)

    def test_venda_cliente_inexistente_retorna_erro(self):
        response = self.client_api.post('/api/vendas/', {
            'cliente_id': 9999,
            'itens': [
                {'produto_id': self.produto.id, 'quantidade': 1}
            ]
        }, format='json')

        self.assertEqual(response.status_code, 400)

    def test_listar_vendas(self):
        Venda.objects.create(cliente=self.cliente, usuario=self.user, valor_total=50)
        response = self.client_api.get('/api/vendas/')
        self.assertEqual(response.status_code, 200)

    # --- Relatórios ---

    def test_relatorio_vendas_periodo(self):
        response = self.client_api.get('/api/relatorios/vendas/?inicio=2020-01-01&fim=2030-12-31')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_vendido', response.data)
        self.assertIn('quantidade_vendas', response.data)

    def test_relatorio_vendas_cliente(self):
        response = self.client_api.get(f'/api/relatorios/vendas-cliente/{self.cliente.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_vendido', response.data)

    def test_relatorio_vendas_anuais(self):
        response = self.client_api.get('/api/relatorios/vendas-anuais/?ano=2026')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['dados']), 12)

    def test_relatorio_produtos_mais_vendidos(self):
        response = self.client_api.get('/api/relatorios/produtos-mais-vendidos/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('produtos', response.data)

    # --- Autenticação ---

    def test_acesso_sem_token_retorna_401(self):
        client_sem_auth = APIClient()
        response = client_sem_auth.get('/api/clientes/')
        self.assertEqual(response.status_code, 401)
