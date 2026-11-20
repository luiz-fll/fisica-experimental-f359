"""Visualizações a partir de resultados já calculados.

Não recalcula períodos, ajustes ou estatísticas. Todas as figuras incluem unidades e o
identificador da filmagem e são salvas na pasta de resultados da filmagem.

Contratos (a implementar):

- ``plotar_angulo_mergulhos(tracker, mergulhadas, id_filmagem, caminho)``
- ``plotar_massa_ajuste(massa, ajuste_global, id_filmagem, caminho)``
- ``plotar_periodo_tempo(ciclos, id_filmagem, caminho)``
- ``plotar_periodo_massa(ciclos, id_filmagem, caminho)`` (exploratório)

Gráficos sem dados suficientes não são gerados; o motivo é registrado no resumo.
"""

from __future__ import annotations
