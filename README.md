# InfoControl – Backend (Entrega 2)

Sistema de Gestão Comercial para loja de informática. API REST para gerenciamento de vendas, estoque, clientes e relatórios.

## Integrantes

- Iorran Valença
- Gabriel Pereira

## Tecnologias

- Python 3.x
- Django 5.0
- Django REST Framework 3.15
- Simple JWT (autenticação por token)
- SQLite (banco integrado, sem configuração adicional)

## Como executar

```bash
cd infocontrol_backend

# Instalar dependências
pip install -r requirements.txt

# Criar o banco e aplicar migrações
python manage.py migrate

# Criar superusuário para acesso inicial
python manage.py createsuperuser

# Rodar o servidor
python manage.py runserver
```

A API estará disponível em `http://127.0.0.1:8000/`.

## Como rodar os testes

```bash
cd infocontrol_backend
python manage.py test core
```

---

## Autenticação

Todas as rotas exigem autenticação via JWT (Bearer Token).

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/login/` | Obter tokens de acesso e refresh |
| POST | `/api/auth/refresh/` | Renovar token de acesso |

**Exemplo de login:**
```json
POST /api/auth/login/
{
  "username": "admin",
  "password": "sua_senha"
}
```

**Uso do token:**
```
Authorization: Bearer <access_token>
```

---

## Clientes (CRUD completo)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/clientes/` | Listar todos os clientes |
| POST | `/api/clientes/` | Cadastrar novo cliente |
| GET | `/api/clientes/{id}/` | Detalhar cliente |
| PUT | `/api/clientes/{id}/` | Atualizar cliente |
| PATCH | `/api/clientes/{id}/` | Atualizar parcialmente |
| DELETE | `/api/clientes/{id}/` | Remover cliente (bloqueado se tiver vendas) |

**Campos:**
```json
{
  "nome": "João Silva",
  "cpf": "12345678901",
  "email": "joao@email.com",
  "telefone": "61999999999",
  "endereco": "Brasília"
}
```

---

## Produtos (CRUD completo + controle de estoque)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/produtos/` | Listar todos os produtos |
| POST | `/api/produtos/` | Cadastrar novo produto |
| GET | `/api/produtos/{id}/` | Detalhar produto |
| PUT | `/api/produtos/{id}/` | Atualizar produto |
| PATCH | `/api/produtos/{id}/` | Atualizar parcialmente |
| DELETE | `/api/produtos/{id}/` | Remover produto (bloqueado se tiver vendas) |
| GET | `/api/produtos/estoque-baixo/` | Listar produtos com estoque abaixo do mínimo |

**Campos:**
```json
{
  "nome": "Mouse Gamer",
  "descricao": "Mouse USB sem fio",
  "preco": "199.90",
  "quantidade_estoque": 20,
  "estoque_minimo": 3
}
```

O campo `estoque_baixo` é retornado automaticamente (`true` quando `quantidade_estoque <= estoque_minimo`).

---

## Vendas (Registro + consulta)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/vendas/` | Registrar nova venda |
| GET | `/api/vendas/` | Listar todas as vendas |
| GET | `/api/vendas/{id}/` | Detalhar venda |

O registro de venda desconta automaticamente o estoque dos produtos.

**Exemplo de criação:**
```json
POST /api/vendas/
{
  "cliente_id": 1,
  "itens": [
    { "produto_id": 1, "quantidade": 2 },
    { "produto_id": 3, "quantidade": 1 }
  ]
}
```

---

## Relatórios

| Método | Endpoint | Parâmetros | Descrição |
|--------|----------|------------|-----------|
| GET | `/api/relatorios/vendas/` | `inicio`, `fim` (YYYY-MM-DD) | Vendas por período |
| GET | `/api/relatorios/vendas-cliente/{id}/` | — | Vendas por cliente |
| GET | `/api/relatorios/vendas-anuais/` | `ano` (ex: 2026) | Vendas mensais do ano |
| GET | `/api/relatorios/produtos-mais-vendidos/` | — | Produtos mais vendidos |

---

## Tratamento de erros

A API usa um handler global de exceções. Erros de negócio retornam HTTP 400 com o formato:

```json
{
  "erro": "Mensagem descritiva do erro"
}
```

Exemplos de erros tratados:
- Estoque insuficiente ao registrar venda
- Cliente não encontrado
- Produto não encontrado
- Tentativa de remover cliente com vendas vinculadas
- Tentativa de remover produto vinculado a vendas

---

## Segurança

- Autenticação via JWT (access token + refresh token)
- Controle de acesso por perfil (ADMIN, FUNCIONARIO)
- Todas as rotas protegidas por padrão

---

## Estrutura do projeto

```
infocontrol_backend/
├── infocontrol/         # Configurações do projeto (settings, urls)
├── core/                # App principal
│   ├── models.py        # Modelos: Cliente, Produto, Venda, ItemVenda
│   ├── serializers.py   # Serializers DRF
│   ├── views.py         # ViewSets e endpoints
│   ├── services.py      # Regras de negócio (VendaService, RelatorioService)
│   ├── exceptions.py    # Exceções personalizadas e handler global
│   ├── permissions.py   # Permissão IsAdminPerfil
│   ├── urls.py          # Rotas do app
│   └── tests.py         # Testes automatizados (21 casos)
├── manage.py
└── requirements.txt
```
