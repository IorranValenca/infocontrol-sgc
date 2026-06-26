"""Autenticacao: login JWT com perfil, controle de acesso e recuperacao de senha.

Fluxo de recuperacao de senha por e-mail:
  1. POST /api/auth/recuperar-senha/  -> envia e-mail com 'uid' e 'token'.
  2. POST /api/auth/redefinir-senha/  -> valida uid+token e grava a nova senha.
"""
from django.contrib.auth.models import User                         # Usuario padrao do Django
from django.contrib.auth.tokens import default_token_generator      # Gera/valida token de redefinicao de senha
from django.core.mail import send_mail                              # Envia e-mails
from django.utils.encoding import force_bytes, force_str            # Converte texto <-> bytes com seguranca
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  # Codifica o id do usuario para a URL
from rest_framework import status                                   # Codigos HTTP (200, 400...)
from rest_framework.decorators import api_view, permission_classes  # Transformam funcoes em endpoints da API
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated  # Regras de acesso
from rest_framework.response import Response                        # Resposta JSON
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  # Serializer padrao do login JWT
from rest_framework_simplejwt.views import TokenObtainPairView      # View padrao do login JWT
from .exceptions import RegraNegocioException
from .models import PerfilUsuario


def perfil_do(usuario):
    """Devolve o perfil do usuario ('ADMIN' para superusuario ou perfil cadastrado)."""
    # Todo superusuario do Django e tratado como ADMIN.
    if usuario.is_superuser:
        return "ADMIN"
    # Caso contrario, le o perfil cadastrado; se nao houver, assume FUNCIONARIO.
    return getattr(getattr(usuario, "perfil_usuario", None), "perfil", "FUNCIONARIO")


def dados_usuario(usuario):
    """Serializa os dados de um usuario para a tela de equipe."""
    return {
        "id": usuario.id,
        "username": usuario.username,
        "email": usuario.email,
        "perfil": perfil_do(usuario),
        "ativo": usuario.is_active,
        "superusuario": usuario.is_superuser,
    }


def validar_perfil(perfil):
    """Normaliza e valida o perfil recebido pela API."""
    perfil = (perfil or "FUNCIONARIO").upper()
    if perfil not in dict(PerfilUsuario.PERFIS):
        raise RegraNegocioException("Perfil invalido.")
    return perfil


def salvar_perfil(usuario, perfil):
    """Grava o perfil funcional usado pelo controle de acesso da API."""
    if usuario.is_superuser:
        return
    PerfilUsuario.objects.update_or_create(usuario=usuario, defaults={"perfil": perfil})


def valor_booleano(valor, padrao=True):
    """Converte booleanos vindos como JSON ou texto."""
    if valor is None:
        return padrao
    if isinstance(valor, str):
        return valor.lower() not in ("false", "0", "nao")
    return bool(valor)


class IsAdminPerfil(BasePermission):
    """Permite o acesso apenas a usuarios com perfil ADMIN (usado para excluir registros)."""

    def has_permission(self, request, view):
        """Retorna True somente se o usuario autenticado for ADMIN."""
        # Precisa estar logado E ter perfil ADMIN.
        return bool(request.user and request.user.is_authenticated and perfil_do(request.user) == "ADMIN")


class LoginSerializer(TokenObtainPairSerializer):
    """Serializer de login que tambem devolve o perfil junto com os tokens."""

    def validate(self, attrs):
        """Valida usuario/senha e acrescenta o campo 'perfil' na resposta."""
        data = super().validate(attrs)          # Gera os tokens 'access' e 'refresh' (logica padrao)
        data["perfil"] = perfil_do(self.user)   # Adiciona o perfil do usuario que acabou de logar
        return data


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ -> recebe username e senha, devolve access, refresh e perfil."""
    serializer_class = LoginSerializer          # Usa o serializer customizado acima


@api_view(["GET"])                              # Endpoint que responde a requisicoes GET
@permission_classes([IsAuthenticated])          # Exige usuario autenticado
def usuario_logado(request):
    """GET /api/auth/me/ -> dados do usuario autenticado (usado pela interface web)."""
    return Response(dados_usuario(request.user))


@api_view(["GET", "POST"])
@permission_classes([IsAdminPerfil])
def equipe(request):
    """GET/POST /api/equipe/ -> lista e cria usuarios da equipe (somente ADMIN)."""
    if request.method == "GET":
        usuarios = User.objects.all().order_by("id")
        return Response([dados_usuario(usuario) for usuario in usuarios])

    username = (request.data.get("username") or "").strip()
    email = (request.data.get("email") or "").strip()
    senha = request.data.get("password") or request.data.get("senha")
    perfil = validar_perfil(request.data.get("perfil"))

    if not username:
        raise RegraNegocioException("Informe o usuario.")
    if not senha:
        raise RegraNegocioException("Informe a senha.")
    if User.objects.filter(username=username).exists():
        raise RegraNegocioException("Usuario ja existe.")

    usuario = User.objects.create_user(username=username, email=email, password=senha)
    usuario.is_active = valor_booleano(request.data.get("ativo"), True)
    usuario.save()
    salvar_perfil(usuario, perfil)
    return Response(dados_usuario(usuario), status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAdminPerfil])
def equipe_detalhe(request, usuario_id):
    """GET/PUT/PATCH /api/equipe/{id}/ -> consulta ou atualiza usuario da equipe."""
    usuario = User.objects.filter(id=usuario_id).first()
    if not usuario:
        raise RegraNegocioException("Usuario nao encontrado.")

    if request.method == "GET":
        return Response(dados_usuario(usuario))

    username = request.data.get("username")
    if username is not None:
        username = username.strip()
        if not username:
            raise RegraNegocioException("Informe o usuario.")
        if User.objects.exclude(id=usuario.id).filter(username=username).exists():
            raise RegraNegocioException("Usuario ja existe.")
        usuario.username = username

    if "email" in request.data:
        usuario.email = (request.data.get("email") or "").strip()

    senha = request.data.get("password") or request.data.get("senha")
    if senha:
        usuario.set_password(senha)

    if "ativo" in request.data:
        ativo = valor_booleano(request.data.get("ativo"), True)
        if usuario.id == request.user.id and not ativo:
            raise RegraNegocioException("Voce nao pode desativar seu proprio usuario.")
        usuario.is_active = ativo

    if "perfil" in request.data:
        perfil = validar_perfil(request.data.get("perfil"))
        if usuario.id == request.user.id and perfil != "ADMIN":
            raise RegraNegocioException("Voce nao pode remover seu proprio perfil ADMIN.")
        salvar_perfil(usuario, perfil)

    usuario.save()
    return Response(dados_usuario(usuario))


@api_view(["POST"])                             # Endpoint que responde a requisicoes POST
@permission_classes([AllowAny])                 # Publico: quem esqueceu a senha ainda nao esta logado
def recuperar_senha(request):
    """Gera um token de redefinicao e o envia para o e-mail informado."""
    email = request.data.get("email")           # E-mail enviado pelo usuario
    usuario = User.objects.filter(email=email).first()  # Procura o usuario com esse e-mail
    if usuario:
        uid = urlsafe_base64_encode(force_bytes(usuario.pk))    # Id do usuario codificado para a URL
        token = default_token_generator.make_token(usuario)     # Token temporario e seguro
        send_mail(                                              # Dispara o e-mail (no terminal, em dev)
            "InfoControl - Recuperacao de senha",               # Assunto
            f"Para redefinir sua senha, informe estes dados:\n\nuid: {uid}\ntoken: {token}",  # Corpo
            None, [email], fail_silently=True,                  # Remetente padrao, destinatario, ignora falhas
        )
    # Resposta generica: nao revela se o e-mail existe (boa pratica de seguranca).
    return Response({"mensagem": "Se o e-mail estiver cadastrado, enviamos as instrucoes."})


@api_view(["POST"])
@permission_classes([AllowAny])                 # Publico: o usuario ainda esta redefinindo a senha
def redefinir_senha(request):
    """Valida uid+token recebidos por e-mail e grava a nova senha."""
    try:
        # Decodifica o uid de volta para o id e busca o usuario correspondente.
        usuario = User.objects.get(pk=force_str(urlsafe_base64_decode(request.data.get("uid", ""))))
    except (User.DoesNotExist, ValueError, TypeError):
        return Response({"erro": "Link de recuperacao invalido."}, status=status.HTTP_400_BAD_REQUEST)

    # Confere se o token confere com o usuario e ainda nao expirou.
    if not default_token_generator.check_token(usuario, request.data.get("token", "")):
        return Response({"erro": "Token invalido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)

    usuario.set_password(request.data.get("nova_senha"))    # Grava a nova senha (ja com hash)
    usuario.save()
    return Response({"mensagem": "Senha redefinida com sucesso."})
