"""Views da interface web: apenas entregam as paginas HTML.

Os dados sao carregados no navegador via JavaScript (fetch), consumindo a API REST.
Por isso cada view so renderiza um template, sem logica de negocio.
"""
from django.shortcuts import render


def pagina(template):
    """Cria uma view que renderiza o template informado (fabrica de views simples)."""
    def view(request):
        return render(request, f"web/{template}.html")
    return view


# Uma view por tela do sistema.
login = pagina("login")
recuperar = pagina("recuperar")
dashboard = pagina("dashboard")
clientes = pagina("clientes")
produtos = pagina("produtos")
vendas = pagina("vendas")
relatorios = pagina("relatorios")
equipe = pagina("equipe")
