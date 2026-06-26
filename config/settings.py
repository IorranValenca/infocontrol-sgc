"""Configuracoes do projeto InfoControl (Sistema de Gestao Comercial)."""
from pathlib import Path            # Manipula caminhos de arquivos de forma multiplataforma
from datetime import timedelta      # Define o tempo de vida dos tokens JWT

# Pasta raiz do projeto (onde fica o manage.py). Serve de base para outros caminhos.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguranca basica ---
SECRET_KEY = "infocontrol-dev-secret-key-troque-em-producao-0123456789abcdef"  # Chave de criptografia (use variavel de ambiente em producao)
DEBUG = True                        # True mostra erros detalhados (apenas em desenvolvimento)
ALLOWED_HOSTS = ["*"]               # Hosts autorizados ("*" = qualquer um, so para desenvolvimento)

# --- Aplicacoes instaladas ---
INSTALLED_APPS = [
    "django.contrib.admin",         # Painel administrativo (/admin/)
    "django.contrib.auth",          # Sistema de usuarios, senhas e permissoes
    "django.contrib.contenttypes",  # Suporte interno do Django aos modelos
    "django.contrib.sessions",      # Sessoes (necessario para o admin)
    "django.contrib.messages",      # Mensagens do admin
    "django.contrib.staticfiles",   # Arquivos estaticos (CSS/JS do admin)
    "rest_framework",               # Django REST Framework (cria a API)
    "api",                          # Nosso app de regras de negocio e endpoints REST
    "web",                          # Nosso app de interface web (telas HTML)
]

# Middlewares: camadas que processam toda requisicao/resposta (seguranca, sessao, etc.).
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"                    # Arquivo de rotas principal
WSGI_APPLICATION = "config.wsgi.application"     # Ponto de entrada para servidores web

# Configuracao do sistema de templates (HTML).
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],                 # Sem pastas extras: cada app guarda seus templates
        "APP_DIRS": True,           # Carrega templates de cada app (web/templates/...)
        "OPTIONS": {
            "context_processors": [  # Variaveis disponiveis em todos os templates
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Banco de dados (SQLite: nao precisa instalar nada) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Banco SQLite (troque por postgresql se quiser)
        "NAME": BASE_DIR / "db.sqlite3",         # Arquivo do banco, criado pelo comando migrate
    }
}

# --- Internacionalizacao ---
LANGUAGE_CODE = "pt-br"             # Idioma do sistema
TIME_ZONE = "America/Sao_Paulo"    # Fuso horario
USE_I18N = True                    # Habilita traducoes
USE_TZ = True                      # Trabalha com datas/horas com fuso

STATIC_URL = "static/"             # URL base dos arquivos estaticos
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # Tipo padrao das chaves primarias (id)

# --- API REST: autenticacao por token JWT e handler global de erros ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # Autenticacao via token JWT
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",                 # Por padrao, exige login em tudo
    ),
    "EXCEPTION_HANDLER": "api.exceptions.handler_global",             # Padroniza as respostas de erro
}

# Tempo de vida dos tokens JWT (requisito: token com expiracao).
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),   # Token de acesso vale 60 minutos
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),      # Token de renovacao vale 1 dia
}

# --- E-mail (recuperacao de senha) ---
# Em desenvolvimento o e-mail e impresso no terminal do runserver (nao envia de verdade).
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "InfoControl <nao-responda@infocontrol.com>"   # Remetente padrao dos e-mails
