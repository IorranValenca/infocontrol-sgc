"""Excecao de negocio e tratamento global de erros da API.

Toda resposta de erro sai no mesmo formato JSON: {"erro": "<mensagem>"}.
Isso e configurado em settings.py (REST_FRAMEWORK -> EXCEPTION_HANDLER).
"""
from rest_framework.views import exception_handler   # Tratamento de erros padrao do DRF
from rest_framework.response import Response          # Resposta JSON
from rest_framework import status                     # Codigos HTTP


class RegraNegocioException(Exception):
    """Erro de regra de negocio (ex.: estoque insuficiente). Vira HTTP 400."""

    def __init__(self, mensagem):
        self.mensagem = mensagem        # Mensagem amigavel mostrada ao usuario
        super().__init__(mensagem)


def handler_global(exc, context):
    """Converte qualquer excecao em uma resposta JSON padronizada com a chave 'erro'."""
    # 1) Erros de negocio retornam 400 com a mensagem amigavel.
    if isinstance(exc, RegraNegocioException):
        return Response({"erro": exc.mensagem}, status=status.HTTP_400_BAD_REQUEST)

    # 2) Demais erros usam o tratamento padrao do DRF, mas embrulhados em {"erro": ...}.
    resposta = exception_handler(exc, context)
    if resposta is not None:
        resposta.data = {"erro": resposta.data}
    return resposta
