from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

class RegraNegocioException(Exception):
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(mensagem)

def custom_exception_handler(exc, context):
    if isinstance(exc, RegraNegocioException):
        return Response(
            {'erro': exc.mensagem},
            status=status.HTTP_400_BAD_REQUEST
        )

    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'erro': response.data
        }

    return response
