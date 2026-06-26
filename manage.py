#!/usr/bin/env python
"""Utilitario de linha de comando do Django (runserver, migrate, test, etc.)."""
import os
import sys


def main():
    """Carrega as configuracoes do projeto e executa o comando recebido no terminal."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # Indica onde estao as configuracoes
    from django.core.management import execute_from_command_line        # Funcao que roda os comandos do Django
    execute_from_command_line(sys.argv)                                 # Executa o comando digitado no terminal


if __name__ == "__main__":
    main()
