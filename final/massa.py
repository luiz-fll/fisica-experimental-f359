"""Ajustes da massa, taxas de variação e diagnósticos.

Modelo: ``m(t) = a + b t``, com ``b`` em g/s.

Taxas:

- Se ``b < 0``: taxa positiva de perda ``r = -b`` [g/s] e ``r_min = -60 b`` [g/min]
  (tipo ``"perda"``).
- Se ``b >= 0``: a inclinação é reportada em ``b_g_s`` sem ser chamada de taxa positiva
  de evaporação. Taxas ficam ausentes (tipo ``"inclinacao_nao_negativa"``).

Mínimos e política de janelas (documentados e configuráveis):

- ``MIN_LEITURAS_AJUSTE = 3``: número mínimo de leituras finitas, com tempos distintos,
  para estimar ``a`` e ``b``. Abaixo disso o ajuste não é feito: ``status`` é
  ``leituras_insuficientes`` e os valores ajustados são NaN. A janela continua na tabela.
- ``LEITURAS_RECOMENDADAS_AJUSTE = 5``: com menos leituras, o ajuste é calculado, mas
  recebe o diagnóstico ``poucos_pontos`` (com 3 ou 4 pontos restam 1 ou 2 graus de
  liberdade residuais).

Diagnósticos (``diagnosticos``, lista de rótulos):

- ``poucos_pontos``: ajuste calculado com menos de ``LEITURAS_RECOMENDADAS_AJUSTE`` leituras.
- ``massa_constante``: todas as leituras iguais; R² é indefinido e fica NaN.
- ``sem_graus_de_liberdade``: duas leituras (``min_leituras=2``); a reta é exata, mas o
  erro padrão de ``b`` e dos resíduos é indefinido e fica NaN.

R² é diagnóstico auxiliar, nunca critério isolado. Os erros padrão de ``b`` e dos
resíduos acompanham a estimativa. Nenhum filtro, remoção de outliers ou suavização é
aplicado; as observações não são alteradas.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from final.periodos import atribuir_janela

MIN_LEITURAS_AJUSTE: int = 3
LEITURAS_RECOMENDADAS_AJUSTE: int = 5

COLUNAS_AJUSTE_JANELA: tuple[str, ...] = (
    "janela",
    "inicio_s",
    "fim_s",
    "n_leituras",
    "a_g",
    "b_g_s",
    "tipo_taxa",
    "taxa_g_s",
    "taxa_g_min",
    "r2",
    "erro_padrao_b_g_s",
    "erro_padrao_residuos_g",
    "residuo_max_abs_g",
    "status",
    "diagnosticos",
)


def _resultado_ajuste(
    n: int, status: str, diagnosticos: list[str], residuos: np.ndarray | None = None
) -> dict:
    """Estrutura de retorno comum de ``ajustar_linear``, com valores ausentes."""
    return {
        "n": n,
        "a_g": np.nan,
        "b_g_s": np.nan,
        "r2": np.nan,
        "erro_padrao_b_g_s": np.nan,
        "erro_padrao_residuos_g": np.nan,
        "residuo_max_abs_g": np.nan,
        "residuos_g": residuos if residuos is not None else np.full(n, np.nan),
        "status": status,
        "diagnosticos": diagnosticos,
    }


def ajustar_linear(
    tempos_s: np.ndarray,
    massas_g: np.ndarray,
    min_leituras: int = MIN_LEITURAS_AJUSTE,
) -> dict:
    """Ajusta ``m(t) = a + b t`` por mínimos quadrados ordinários.

    Retorna um dicionário com ``n``, ``a_g``, ``b_g_s``, ``r2``, ``erro_padrao_b_g_s``,
    ``erro_padrao_residuos_g`` (``sqrt(SSres/(n-2))``), ``residuo_max_abs_g``,
    ``residuos_g`` (observado menos ajustado, alinhado às entradas), ``status`` (``ok``,
    ``leituras_insuficientes`` ou ``sem_variacao_temporal``) e ``diagnosticos``.

    Levanta ``ValueError`` para entradas de tamanhos diferentes, não finitas ou com
    ``min_leituras < 2``. Não altera as observações de entrada.
    """
    t = np.asarray(tempos_s, dtype=float)
    m = np.asarray(massas_g, dtype=float)
    if t.ndim != 1 or t.shape != m.shape:
        raise ValueError("tempos_s e massas_g devem ser vetores de mesmo tamanho")
    if not (np.all(np.isfinite(t)) and np.all(np.isfinite(m))):
        raise ValueError("tempos_s e massas_g devem ser finitos")
    if min_leituras < 2:
        raise ValueError("min_leituras deve ser pelo menos 2")

    n = int(t.size)
    if n < min_leituras:
        return _resultado_ajuste(n, "leituras_insuficientes", [])
    if np.unique(t).size < 2:
        return _resultado_ajuste(n, "sem_variacao_temporal", [])

    t_medio = t.mean()
    m_medio = m.mean()
    sxx = float(np.sum((t - t_medio) ** 2))
    sxy = float(np.sum((t - t_medio) * (m - m_medio)))
    b = sxy / sxx
    a = m_medio - b * t_medio

    residuos = m - (a + b * t)
    ss_res = float(np.sum(residuos**2))
    ss_tot = float(np.sum((m - m_medio) ** 2))

    diagnosticos: list[str] = []
    if n < LEITURAS_RECOMENDADAS_AJUSTE:
        diagnosticos.append("poucos_pontos")
    if ss_tot == 0.0:
        diagnosticos.append("massa_constante")
        r2 = np.nan
    else:
        r2 = 1.0 - ss_res / ss_tot

    if n > 2:
        erro_padrao_residuos = float(np.sqrt(ss_res / (n - 2)))
        erro_padrao_b = erro_padrao_residuos / float(np.sqrt(sxx))
    else:
        # Com 2 leituras não há graus de liberdade residuais: o erro padrão é indefinido.
        diagnosticos.append("sem_graus_de_liberdade")
        erro_padrao_residuos = np.nan
        erro_padrao_b = np.nan
    return {
        "n": n,
        "a_g": float(a),
        "b_g_s": float(b),
        "r2": float(r2),
        "erro_padrao_b_g_s": erro_padrao_b,
        "erro_padrao_residuos_g": erro_padrao_residuos,
        "residuo_max_abs_g": float(np.max(np.abs(residuos))),
        "residuos_g": residuos,
        "status": "ok",
        "diagnosticos": diagnosticos,
    }


def taxa_de_perda(b_g_s: float) -> dict:
    """Converte a inclinação ``b`` (g/s) na taxa positiva de perda.

    - ``b < 0``: tipo ``"perda"``, ``taxa_g_s = -b`` e ``taxa_g_min = -60 b``.
    - ``b >= 0``: tipo ``"inclinacao_nao_negativa"``; taxas NaN, ``b_g_s`` preservado.
    - ``b`` não finito: tipo ``"indefinido"``; tudo NaN.
    """
    b = float(b_g_s)
    if not np.isfinite(b):
        return {"b_g_s": np.nan, "tipo_taxa": "indefinido", "taxa_g_s": np.nan, "taxa_g_min": np.nan}
    if b < 0:
        return {"b_g_s": b, "tipo_taxa": "perda", "taxa_g_s": -b, "taxa_g_min": -60.0 * b}
    return {
        "b_g_s": b,
        "tipo_taxa": "inclinacao_nao_negativa",
        "taxa_g_s": np.nan,
        "taxa_g_min": np.nan,
    }


def ajustar_janelas(
    massa: pd.DataFrame,
    limites: pd.DataFrame,
    min_leituras: int = MIN_LEITURAS_AJUSTE,
) -> pd.DataFrame:
    """Ajusta a massa em cada janela fixa de ``limites``, sem misturar janelas.

    Cada leitura pertence à janela que a contém (``atribuir_janela``). Todas as janelas
    aparecem na saída, na ordem de ``limites``. Janelas com menos de ``min_leituras``
    leituras têm ``status`` ``leituras_insuficientes`` e valores ausentes. Colunas em
    ``COLUNAS_AJUSTE_JANELA``; ``diagnosticos`` é uma string separada por ``;``.
    """
    atribuidas = atribuir_janela(massa["tempo_seg"], limites)
    tempos = massa["tempo_seg"].to_numpy(dtype=float)
    massas = massa["massa_g"].to_numpy(dtype=float)

    linhas = []
    for _, limite in limites.iterrows():
        mascara = np.array(
            [pd.notna(v) and int(v) == int(limite["janela"]) for v in atribuidas],
            dtype=bool,
        )
        ajuste = ajustar_linear(tempos[mascara], massas[mascara], min_leituras=min_leituras)
        taxa = taxa_de_perda(ajuste["b_g_s"])
        linhas.append(
            {
                "janela": int(limite["janela"]),
                "inicio_s": float(limite["inicio_s"]),
                "fim_s": float(limite["fim_s"]),
                "n_leituras": ajuste["n"],
                "a_g": ajuste["a_g"],
                "b_g_s": taxa["b_g_s"],
                "tipo_taxa": taxa["tipo_taxa"],
                "taxa_g_s": taxa["taxa_g_s"],
                "taxa_g_min": taxa["taxa_g_min"],
                "r2": ajuste["r2"],
                "erro_padrao_b_g_s": ajuste["erro_padrao_b_g_s"],
                "erro_padrao_residuos_g": ajuste["erro_padrao_residuos_g"],
                "residuo_max_abs_g": ajuste["residuo_max_abs_g"],
                "status": ajuste["status"],
                "diagnosticos": ";".join(ajuste["diagnosticos"]),
            }
        )
    return pd.DataFrame(linhas, columns=list(COLUNAS_AJUSTE_JANELA))
