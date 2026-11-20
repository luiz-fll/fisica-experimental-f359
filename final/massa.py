"""Ajustes da massa, taxas de variação e diagnósticos.

Modelo: ``m(t) = a + b t``, com ``b`` em g/s.

Taxas (contrato):

- Se ``b < 0``: taxa positiva de perda ``r = -b`` [g/s] e ``r_min = -60 b`` [g/min].
- Se ``b >= 0``: reportar a inclinação ``b`` sem chamá-la de taxa positiva de evaporação.

Mínimos e política de janelas (documentados e configuráveis):

- ``MIN_LEITURAS_AJUSTE = 3``: número mínimo de leituras finitas, com tempos distintos,
  para estimar ``a`` e ``b``. Abaixo disso o ajuste local não é feito e a janela recebe
  o status ``leituras_insuficientes`` (a linha é mantida na tabela, sem valores ajustados).
- ``LEITURAS_RECOMENDADAS_AJUSTE = 5``: abaixo deste número o ajuste é calculado, mas
  recebe o diagnóstico ``poucos_pontos`` (com 3 pontos há apenas 1 grau de liberdade
  residual, insuficiente para avaliar o ajuste).

R² é diagnóstico auxiliar; não é critério isolado. Nenhum filtro, remoção de outliers
ou suavização é aplicado por padrão.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

MIN_LEITURAS_AJUSTE: int = 3
LEITURAS_RECOMENDADAS_AJUSTE: int = 5


def ajustar_linear(tempos_s: np.ndarray, massas_g: np.ndarray) -> dict:
    """Ajusta ``m(t) = a + b t`` por mínimos quadrados (contrato).

    Retorna um dicionário com ``a_g``, ``b_g_s``, ``n``, ``r2``, ``residuos_g`` (observado
    menos ajustado), ``status`` e ``diagnosticos``. Não altera as observações de entrada.
    """
    raise NotImplementedError("ajustar_linear: a implementar na etapa de massa.")


def taxa_de_perda(b_g_s: float) -> dict:
    """Converte a inclinação em taxa de perda (contrato).

    Para ``b < 0`` retorna ``taxa_g_s = -b`` e ``taxa_g_min = -60 b``. Para ``b >= 0``
    retorna ``taxa_g_s`` e ``taxa_g_min`` ausentes e preserva ``b_g_s``.
    """
    raise NotImplementedError("taxa_de_perda: a implementar na etapa de massa.")


def ajustar_janelas(
    massa: pd.DataFrame,
    limites: pd.DataFrame,
    min_leituras: int = MIN_LEITURAS_AJUSTE,
) -> pd.DataFrame:
    """Ajusta a massa em cada janela fixa de ``limites`` (contrato).

    Todas as janelas aparecem na saída. Janelas com menos de ``min_leituras`` leituras
    recebem o status ``leituras_insuficientes`` e valores ausentes.
    """
    raise NotImplementedError("ajustar_janelas: a implementar na etapa de massa.")
