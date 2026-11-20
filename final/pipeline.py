"""Orquestração do processamento de uma filmagem.

Contrato (a implementar):

``processar_filmagem(filmagem: dict, duracao_janela_s: float, pasta_saida: Path) -> dict``

- ``filmagem`` é o dicionário já validado produzido por ``analisar.carregar_filmagem``,
  com as chaves ``id`` (str), ``pasta`` (Path), ``tracker``, ``massa``, ``mergulhadas``
  (DataFrames com colunas originais) e ``condicoes`` (dict de uma linha).
- Não lê arquivos: a leitura é responsabilidade de ``analisar.py``.
- Retorna um dicionário com ``id``, ``status``, ``diagnosticos`` e os DataFrames
  calculados. Escreve saídas somente em ``pasta_saida``.
"""

from __future__ import annotations

from pathlib import Path


def processar_filmagem(filmagem: dict, duracao_janela_s: float, pasta_saida: Path) -> dict:
    """Processa uma filmagem válida (contrato)."""
    raise NotImplementedError("processar_filmagem: a implementar na etapa de pipeline.")
