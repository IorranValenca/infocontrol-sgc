"""Testes automatizados da API (autenticacao, CRUD, vendas, relatorios, recuperacao de senha)."""
from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient
from .models import Cliente, PerfilUsuario, Produto, Venda


class InfoControlTests(TestCase):
    """Cenarios principais do sistema, todos exercitando a API REST."""

    def setUp(self):
        """Cria um usuario admin autenticado, um cliente e um produto para os testes."""
        self.user = User.objects.create_superuser("admin", "admin@loja.com", "123456")
        self.api = APIClient()
        token = self.api.post("/api/auth/login/", {"username": "admin", "password": "123456"}, format="json").data["access"]
        self.api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.cliente = Cliente.objects.create(nome="Joao", cpf="12345678901", email="joao@email.com")
        self.produto = Produto.objects.create(nome="Mouse", preco=100, quantidade_estoque=10, estoque_minimo=2)

    def cliente_funcionario(self):
        """Cria e autentica um funcionario para testar permissoes de caixa/venda."""
        usuario = User.objects.create_user("caixa", "caixa@loja.com", "123456")
        PerfilUsuario.objects.create(usuario=usuario, perfil="FUNCIONARIO")
        api = APIClient()
        token = api.post("/api/auth/login/", {"username": "caixa", "password": "123456"}, format="json").data["access"]
        api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return api

    # --- Autenticacao ---
    def test_login_retorna_token_e_perfil(self):
        """O login devolve o token de acesso e o perfil do usuario."""
        r = self.api.post("/api/auth/login/", {"username": "admin", "password": "123456"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)
        self.assertEqual(r.data["perfil"], "ADMIN")

    def test_acesso_sem_token_retorna_401(self):
        """Rotas protegidas recusam requisicoes sem token."""
        self.assertEqual(APIClient().get("/api/clientes/").status_code, 401)

    def test_me_retorna_usuario_logado(self):
        """O endpoint /auth/me/ devolve o usuario autenticado."""
        r = self.api.get("/api/auth/me/")
        self.assertEqual(r.data["username"], "admin")

    def test_tela_login_tem_feedback_de_erro(self):
        """A tela de login possui feedback visivel para credenciais invalidas."""
        conteudo = Client().get("/").content
        self.assertIn(b"login-erro", conteudo)
        self.assertIn(b"novalidate", conteudo)
        self.assertIn(b"Informe o usuario", conteudo)
        self.assertIn(b"Usuario nao encontrado ou senha invalida", conteudo)
        self.assertIn(b"authPublica", conteudo)

    def test_admin_cria_funcionario_na_equipe(self):
        """Um ADMIN pode criar usuario funcionario com senha e perfil."""
        r = self.api.post("/api/equipe/", {
            "username": "vendedor", "email": "vendedor@loja.com",
            "password": "123456", "perfil": "FUNCIONARIO",
        }, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["perfil"], "FUNCIONARIO")
        self.assertTrue(User.objects.get(username="vendedor").check_password("123456"))

    def test_admin_atualiza_usuario_da_equipe(self):
        """Um ADMIN pode trocar perfil e status de usuario da equipe."""
        usuario = User.objects.create_user("assistente", "a@loja.com", "123456")
        PerfilUsuario.objects.create(usuario=usuario, perfil="FUNCIONARIO")
        r = self.api.patch(f"/api/equipe/{usuario.id}/", {"perfil": "ADMIN", "ativo": False}, format="json")
        self.assertEqual(r.status_code, 200)
        usuario.refresh_from_db()
        self.assertFalse(usuario.is_active)
        usuario.perfil_usuario.refresh_from_db()
        self.assertEqual(usuario.perfil_usuario.perfil, "ADMIN")

    def test_funcionario_nao_gerencia_equipe(self):
        """Funcionario nao pode acessar a gestao de equipe."""
        self.assertEqual(self.cliente_funcionario().get("/api/equipe/").status_code, 403)

    # --- Clientes ---
    def test_criar_cliente(self):
        """Cadastra um cliente valido (HTTP 201)."""
        r = self.api.post("/api/clientes/", {"nome": "Maria", "cpf": "98765432100", "email": "m@e.com"}, format="json")
        self.assertEqual(r.status_code, 201)

    def test_cpf_invalido_retorna_erro(self):
        """CPF com menos de 11 digitos e rejeitado."""
        r = self.api.post("/api/clientes/", {"nome": "X", "cpf": "123", "email": "x@e.com"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_cliente_com_vendas_nao_pode_ser_removido(self):
        """Cliente com vendas registradas nao pode ser excluido."""
        Venda.objects.create(cliente=self.cliente, usuario=self.user, valor_total=100)
        self.assertEqual(self.api.delete(f"/api/clientes/{self.cliente.id}/").status_code, 400)

    # --- Produtos ---
    def test_criar_produto(self):
        """Cadastra um produto valido (HTTP 201)."""
        r = self.api.post("/api/produtos/", {"nome": "Teclado", "preco": "250.00", "quantidade_estoque": 5}, format="json")
        self.assertEqual(r.status_code, 201)

    def test_preco_negativo_retorna_erro(self):
        """Produto com preco negativo e rejeitado."""
        r = self.api.post("/api/produtos/", {"nome": "Ruim", "preco": "-1", "quantidade_estoque": 1}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_estoque_baixo(self):
        """A consulta de estoque baixo lista produtos no/abaixo do minimo."""
        critico = Produto.objects.create(nome="Critico", preco=10, quantidade_estoque=1, estoque_minimo=5)
        ids = [p["id"] for p in self.api.get("/api/produtos/estoque-baixo/").data]
        self.assertIn(critico.id, ids)

    def test_criar_produto_com_marca_categoria_garantia(self):
        """Produto aceita marca, categoria e garantia (atributos de loja de informatica)."""
        r = self.api.post("/api/produtos/", {
            "nome": "Monitor 24", "marca": "LG", "categoria": "MONITOR",
            "preco": "899.00", "quantidade_estoque": 4, "garantia_meses": 24,
        }, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["categoria"], "MONITOR")
        self.assertEqual(r.data["marca"], "LG")
        self.assertEqual(r.data["garantia_meses"], 24)

    def test_funcionario_le_produtos_mas_nao_altera_catalogo(self):
        """Funcionario pode ler produtos para vender, mas nao cadastrar/editar catalogo."""
        api = self.cliente_funcionario()
        self.assertEqual(api.get("/api/produtos/").status_code, 200)
        r = api.post("/api/produtos/", {"nome": "SSD", "preco": "300.00", "quantidade_estoque": 2}, format="json")
        self.assertEqual(r.status_code, 403)

    # --- Vendas ---
    def test_registrar_venda_baixa_estoque_e_calcula_total(self):
        """Ao vender, o estoque diminui e o valor_total e calculado automaticamente."""
        r = self.api.post("/api/vendas/", {"cliente_id": self.cliente.id,
            "itens": [{"produto_id": self.produto.id, "quantidade": 3}]}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(float(r.data["valor_total"]), 300.0)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade_estoque, 7)

    def test_estoque_insuficiente_retorna_erro(self):
        """Venda acima do estoque disponivel e bloqueada."""
        r = self.api.post("/api/vendas/", {"cliente_id": self.cliente.id,
            "itens": [{"produto_id": self.produto.id, "quantidade": 99}]}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_venda_sem_itens_retorna_erro(self):
        """Venda sem itens e rejeitada."""
        r = self.api.post("/api/vendas/", {"cliente_id": self.cliente.id, "itens": []}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_funcionario_acessa_clientes_e_registra_venda(self):
        """Funcionario consegue usar as areas permitidas: clientes e vendas."""
        api = self.cliente_funcionario()
        self.assertEqual(api.get("/api/clientes/").status_code, 200)
        r = api.post("/api/vendas/", {"cliente_id": self.cliente.id,
            "itens": [{"produto_id": self.produto.id, "quantidade": 1}]}, format="json")
        self.assertEqual(r.status_code, 201)

    # --- Relatorios ---
    def test_relatorio_periodo(self):
        """O relatorio por periodo devolve o total vendido."""
        r = self.api.get("/api/relatorios/vendas/?inicio=2020-01-01&fim=2030-12-31")
        self.assertIn("total_vendido", r.data)

    def test_relatorio_anual_tem_12_meses(self):
        """O relatorio anual devolve um valor para cada mes do ano."""
        r = self.api.get("/api/relatorios/vendas-anuais/?ano=2026")
        self.assertEqual(len(r.data["dados"]), 12)

    def test_relatorio_mais_vendidos(self):
        """O relatorio de mais vendidos lista os produtos com vendas registradas."""
        self.api.post("/api/vendas/", {"cliente_id": self.cliente.id,
            "itens": [{"produto_id": self.produto.id, "quantidade": 2}]}, format="json")
        r = self.api.get("/api/relatorios/mais-vendidos/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.produto.nome, [p["produto"] for p in r.data["produtos"]])

    def test_funcionario_nao_acessa_relatorios(self):
        """Relatorios ficam restritos ao ADMIN."""
        self.assertEqual(self.cliente_funcionario().get("/api/relatorios/vendas/").status_code, 403)

    # --- Recuperacao de senha ---
    def test_recuperar_senha_responde_generico(self):
        """A solicitacao de recuperacao sempre responde 200 (nao revela se o e-mail existe)."""
        r = self.api.post("/api/auth/recuperar-senha/", {"email": "admin@loja.com"}, format="json")
        self.assertEqual(r.status_code, 200)

    def test_redefinir_senha_com_token_valido(self):
        """Com uid+token validos, a nova senha e gravada com sucesso."""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        r = APIClient().post("/api/auth/redefinir-senha/",
            {"uid": uid, "token": token, "nova_senha": "novaSenha123"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("novaSenha123"))
