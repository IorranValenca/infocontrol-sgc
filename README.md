# 🛒 InfoControl — Sistema de Gestão Comercial

Sistema de gestão comercial para uma **loja de informática**. Permite controlar
clientes, produtos, estoque e vendas, com dashboard principal, relatórios e gráficos.
É composto por uma **API REST** (protegida por token JWT) e uma **interface web**
que consome essa API.

> **Identidade visual:** logotipo e nome *InfoControl* com esquema de cores próprio (laranja `#FF751F`).

---

## 🚀 Tutorial: rodando pela primeira vez

> Pré-requisito: ter o **Python 3.10+** instalado. Confira com `python --version`.

Abra o terminal **na pasta do projeto** (onde está o arquivo `manage.py`) e siga os passos:

### 1. Criar e ativar um ambiente virtual
Isola as bibliotecas do projeto das do seu computador.

```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```
> Deu certo quando aparece `(venv)` no início da linha do terminal.

### 2. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 3. Criar o banco de dados
Cria o arquivo `db.sqlite3` e todas as tabelas automaticamente.
```bash
python manage.py migrate
```

### 4. Criar o usuário administrador
Será o seu login no sistema (perfil **ADMIN**).
```bash
python manage.py createsuperuser
```
> Informe um **usuário**, **e-mail** e **senha**. O e-mail é usado na recuperação de senha.

### 5. Iniciar o servidor
```bash
python manage.py runserver
```

### 6. Acessar o sistema
Abra o navegador em **http://127.0.0.1:8000/** e faça login com o usuário criado.
Após o login, o sistema abre o **Dashboard** em **/dashboard/**. 🎉

> Para parar o servidor, pressione `Ctrl + C` no terminal.
> Nas próximas vezes, basta repetir os passos **1 (ativar)** e **5 (runserver)**.

---

## 🖥️ Como usar a interface

| Tela | O que faz |
|------|-----------|
| **Login** | Autentica o usuário, guarda o token JWT no navegador e redireciona para o Dashboard. |
| **Dashboard** | Tela principal com visão geral de clientes, produtos, estoque, vendas, receita, ticket médio, gráfico anual, vendas recentes, produtos mais vendidos, estoque baixo e clientes recentes. Inclui um botão **+** que abre ações rápidas orbitando o botão: cliente, produto e venda. |
| **Clientes** | Cadastra, edita e remove clientes. |
| **Produtos** | Catálogo com **marca**, **categoria** e **garantia**; busca e filtro por categoria, com alerta de *estoque baixo*. |
| **Vendas** | Monta a venda (cliente + itens) e registra; o estoque é baixado automaticamente. |
| **Relatórios** | Relatórios detalhados que abrem já carregados: indicadores, **gráfico** de vendas anuais, vendas por período, **produtos mais vendidos** e itens para repor. |
| **Equipe** | Tela de administradores para criar usuários, definir perfil (**ADMIN** ou **FUNCIONARIO**), trocar senha e ativar/desativar membros. Funcionários veem apenas **Clientes** e **Vendas** no menu. |

### 🔑 Recuperação de senha por e-mail
1. Na tela de login, clique em **"Esqueci minha senha"** e informe o e-mail.
2. Em modo de desenvolvimento o e-mail é **exibido no terminal** onde roda o `runserver`
   (procure por `uid:` e `token:`).
3. Volte à tela de recuperação, informe o **uid**, o **token** e a **nova senha**.

> Para enviar e-mails de verdade, configure um servidor SMTP em `config/settings.py`
> (variável `EMAIL_BACKEND`).

---

## 📂 Organização do projeto

```
infocontrol/
├── manage.py             # Comandos do Django (runserver, migrate, test...)
├── requirements.txt      # Dependências do projeto
├── database/script.sql   # Script SQL do banco (modelagem)
├── docs/                 # Documentação e diagramas
│
├── config/               # ⚙️  Configuração do projeto
│   ├── settings.py       #     Configurações gerais
│   └── urls.py           #     Roteamento principal (admin / api / web)
│
├── api/                  # 🔌 Camada da API REST (regras de negócio)
│   ├── models.py         #     Tabelas: Cliente, Produto, Venda, ItemVenda, PerfilUsuario
│   ├── serializers.py    #     Conversão e validação JSON ⇄ modelo
│   ├── services.py       #     Regras de negócio (vendas e relatórios)
│   ├── views.py          #     Endpoints REST (clientes, produtos, vendas, relatórios)
│   ├── auth.py           #     Login JWT, perfis e recuperação de senha
│   ├── exceptions.py     #     Exceções de negócio + handler global de erros
│   ├── urls.py           #     Rotas da API
│   └── tests.py          #     25 testes automatizados
│
└── web/                  # 🎨 Interface web (consome a API via JavaScript)
    ├── views.py          #     Entrega as páginas HTML
    └── templates/web/    #     Telas: login, dashboard, clientes, produtos, vendas, relatórios, equipe
```

---

## 🌐 API REST

Todas as rotas (exceto login e recuperação de senha) exigem o cabeçalho:
`Authorization: Bearer <token>`. Toda resposta é em **JSON**.

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/login/` | Login → retorna `access`, `refresh` e `perfil` |
| POST | `/api/auth/refresh/` | Renova o token de acesso |
| GET | `/api/auth/me/` | Dados do usuário logado |
| POST | `/api/auth/recuperar-senha/` | Envia e-mail de recuperação |
| POST | `/api/auth/redefinir-senha/` | Redefine a senha (uid + token) |
| GET / POST | `/api/equipe/` | Lista / cria usuários da equipe (**ADMIN**) |
| GET / PUT / PATCH | `/api/equipe/{id}/` | Detalha / edita perfil, senha e status de usuário (**ADMIN**) |
| GET / POST | `/api/clientes/` | Lista / cadastra clientes |
| GET / PUT / DELETE | `/api/clientes/{id}/` | Detalha / edita / remove cliente |
| GET / POST | `/api/produtos/` | Lista produtos para usuários logados / cadastra produtos para **ADMIN** |
| GET / PUT / DELETE | `/api/produtos/{id}/` | Detalha produtos para usuários logados / edita ou remove para **ADMIN** |
| GET | `/api/produtos/estoque-baixo/` | Produtos no/abaixo do estoque mínimo (**ADMIN**) |
| GET / POST | `/api/vendas/` | Lista / registra vendas |
| GET | `/api/vendas/{id}/` | Detalha uma venda |
| GET | `/api/relatorios/vendas/?inicio=&fim=` | Vendas por período |
| GET | `/api/relatorios/vendas-cliente/{id}/` | Vendas de um cliente |
| GET | `/api/relatorios/vendas-anuais/?ano=` | Total mês a mês (gráfico) |
| GET | `/api/relatorios/mais-vendidos/` | Produtos campeões de venda (best-sellers) |

> **Catálogo de informática:** além de nome, preço e estoque, cada produto tem
> **marca**, **categoria** (Notebooks, Componentes, Periféricos, Monitores, etc.) e
> **garantia em meses** — atributos próprios de uma loja de informática.

**Exemplo — registrar venda:**
```json
POST /api/vendas/
{
  "cliente_id": 1,
  "itens": [{ "produto_id": 1, "quantidade": 2 }]
}
```

---

## 🧪 Testes

```bash
python manage.py test
```
> 25 testes cobrindo autenticação, feedback de login, equipe/perfis, CRUD, catálogo, regras de venda, relatórios, permissões de funcionário e recuperação de senha.

---

## 🏛️ Documentação técnica

### Arquitetura em camadas
O projeto separa responsabilidades em camadas, o que facilita a manutenção:

| Camada | Onde | Responsabilidade |
|--------|------|------------------|
| Apresentação | `web/` | Telas HTML que consomem a API. |
| API / Controle | `api/views.py`, `api/urls.py` | Recebe as requisições HTTP e responde JSON. |
| Negócio (serviço) | `api/services.py` | Regras de venda, estoque e relatórios. |
| Persistência | `api/models.py` | Mapeamento objeto-relacional (ORM) com o banco. |

### Padrões de projeto utilizados
- **Service Layer** — regras de negócio isoladas em `services.py`, fora das views.
- **Serializer / DTO** — `serializers.py` valida e converte os dados de entrada/saída.
- **Repository (via ORM)** — o ORM do Django abstrai o acesso ao banco de dados.
- **Exception Handler global** — todos os erros saem no formato padrão `{"erro": ...}`.

### Decisões técnicas
- **Django + DRF**: produtividade e uma API REST robusta com pouco código.
- **JWT (SimpleJWT)**: autenticação sem estado (stateless), ideal para APIs.
- **SQLite**: banco sem instalação, perfeito para desenvolvimento e avaliação
  (pode ser trocado por PostgreSQL apenas alterando `DATABASES` em `settings.py`).
- **Interface desacoplada**: o front consome a API via `fetch`, provando que a
  API funciona de forma independente e poderia servir também um app mobile.

### Segurança
- Autenticação por token **JWT** com expiração.
- Senhas armazenadas com **hash** (PBKDF2, padrão do Django).
- **Controle de acesso por perfil**: **ADMIN** acessa todo o sistema; **FUNCIONARIO** acessa clientes e vendas, com leitura de produtos apenas para registrar vendas.
- Todas as rotas da API são protegidas por padrão.

### Regras de negócio
- CPF único e e-mail válido para clientes.
- Preço e estoque nunca negativos.
- Venda não acontece sem itens ou com estoque insuficiente.
- Estoque é atualizado e o total é calculado automaticamente a cada venda.
- Cliente/produto vinculado a vendas não pode ser excluído.

---

## 🛠️ Tecnologias
- Python 3.12 · Django 6 · Django REST Framework · SimpleJWT (JWT) · SQLite · Chart.js

## 👥 Integrantes
- Iorran Valença
- Gabriel Pereira
