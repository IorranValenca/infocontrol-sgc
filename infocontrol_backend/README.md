# InfoControl - Backend Entrega 2

Sistema de Gestão Comercial para loja de informática.

## Funcionalidades

- Autenticação JWT
- CRUD de clientes
- CRUD de produtos
- Registro de vendas
- Controle automático de estoque
- Relatórios de vendas
- Banco de dados integrado
- Tratamento de exceções
- Testes básicos

## Tecnologias

- Python
- Django
- Django REST Framework
- JWT
- SQLite por padrão, podendo ser alterado para PostgreSQL

## Como rodar

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Endpoints principais

### Autenticação

```http
POST /api/auth/login/
POST /api/auth/refresh/
```

### Clientes

```http
GET /api/clientes/
POST /api/clientes/
GET /api/clientes/{id}/
PUT /api/clientes/{id}/
DELETE /api/clientes/{id}/
```

### Produtos

```http
GET /api/produtos/
POST /api/produtos/
GET /api/produtos/{id}/
PUT /api/produtos/{id}/
DELETE /api/produtos/{id}/
```

### Vendas

```http
GET /api/vendas/
POST /api/vendas/
GET /api/vendas/{id}/
```

### Relatórios

```http
GET /api/relatorios/vendas/?inicio=2026-01-01&fim=2026-12-31
GET /api/relatorios/vendas-cliente/{cliente_id}/
GET /api/relatorios/vendas-anuais/?ano=2026
```

## Exemplo de login

```json
{
  "username": "admin",
  "password": "123456"
}
```

## Exemplo de venda

```json
{
  "cliente_id": 1,
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 2
    }
  ]
}
```

## Observação

Para acessar rotas protegidas, envie o token no header:

```http
Authorization: Bearer SEU_TOKEN
```
