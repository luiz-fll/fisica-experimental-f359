"""CLI, descoberta, leitura e validação das filmagens.

Estado atual: a CLI ainda não está implementada. Esta versão contém somente os
contratos da etapa de entrada, para que os demais módulos tenham assinaturas estáveis.

Contratos (a implementar):

- ``main(argv: list[str] | None = None) -> int``: interpreta
  ``--diretorio``, ``--saida`` e ``--janela`` (duração positiva, em segundos).
- ``descobrir_filmagens(diretorio: Path) -> list[Path]``: subpastas diretas.
- ``carregar_filmagem(pasta: Path) -> dict``: lê e valida os quatro CSVs obrigatórios
  sem modificá-los. Levanta ``ErroFilmagem`` com filmagem e arquivo identificados.

Uma filmagem inválida é reportada e ignorada, sem interromper as demais.
"""

from __future__ import annotations

import sys
from pathlib import Path


class ErroFilmagem(Exception):
    """Erro de validação de uma filmagem, com identificação da pasta e do arquivo."""

    def __init__(self, pasta: Path, arquivo: str, mensagem: str) -> None:
        super().__init__(f"[{pasta.name}] {arquivo}: {mensagem}")
        self.pasta = pasta
        self.arquivo = arquivo
        self.mensagem = mensagem


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI (ainda não implementado)."""
    print("analisar.py: CLI ainda não implementada (etapa de entrada e validação).", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
