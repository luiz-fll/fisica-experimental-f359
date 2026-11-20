"""Exportação de tabelas derivadas e resumos.

Preserva a precisão numérica nos arquivos; arredondamento apenas para apresentação.

Contratos (a implementar):

- ``gravar_tabelas(pasta_saida, tabelas: dict[str, pd.DataFrame]) -> list[Path]``
  grava ``periodos.csv``, ``massa_ajuste.csv``, ``massa_por_janela.csv``,
  ``periodo_por_janela.csv`` e ``resumo.csv``.
- ``gravar_resumo_texto(pasta_saida, resumo: dict) -> Path`` grava ``resumo.txt``.

Nunca grava sobre dados brutos; ``pasta_saida`` deve estar fora de ``final/dados*``.
"""

from __future__ import annotations
