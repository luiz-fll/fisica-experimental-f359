"""Propriedades físicas dos líquidos externos, com fonte NIST, e calor latente efetivo.

Fonte primária: NIST Chemistry WebBook (https://webbook.nist.gov) e JANAF
(https://janaf.nist.gov), consultados em 2026-11-20. Os valores são de 298,15 K (25 °C).
As filmagens ocorreram entre 23,0 e 23,9 °C. Para a água, a variação de ΔvapH com a
temperatura é ΔCp = Cp(gás) − Cp(líquido) ≈ −41,8 J/(mol·K) (JANAF), ou ≈ 0,1 % por
kelvin: a diferença entre 23 e 24 °C é desprezível. Para etanol e isopropanol, o ΔCp
não foi verificado; por isso a dependência de L com T não é corrigida, e isso é uma
limitação declarada.

Dados (todos de NIST):

- Água (H2O): M = 18,015 g/mol. ΔvapH = 44,00 kJ/mol a 298,15 K (JANAF: ΔfH°(g) −241,826
  e ΔfH°(l) −285,830 kJ/mol). Pressão de vapor derivada de ΔfG°(g) −228,582 e
  ΔfG°(l) −237,141 kJ/mol: P = P°·exp(−ΔG/RT), P° = 1 bar.
- Etanol (C2H6O): M = 46,068 g/mol. ΔvapH = 42,3 ± 0,4 kJ/mol (média NIST). Pressão de
  vapor por Antoine NIST (Ambrose & Sprake, 1970; faixa 292,77–366,63 K): A = 5,24677,
  B = 1598,673, C = −46,424, log10(P/bar) = A − B/(T + C).
- Isopropanol (C3H8O), é o "álcool 99 %": M = 60,095 g/mol. ΔvapH = 45 ± 3 kJ/mol
  (média NIST). Pressão de vapor por Antoine NIST (Biddiscombe et al., 1963; faixa
  329,92–362,41 K): A = 4,8610, B = 1357,427, C = −75,814. ATENÇÃO: 298,15 K está fora
  dessa faixa; a pressão é uma extrapolação, usada apenas para a composição do vapor da
  mistura.
- Mistura "álcool 70 %": etanol a 70 % em massa (w/w) em água. A composição do vapor é
  estimada por lei de Raoult ideal a partir das pressões acima. Esta é uma aproximação:
  a mistura real desvia da idealidade e a composição muda com o tempo (o etanol evapora
  primeiro).

Calor latente efetivo L (kJ/kg), ou seja, energia removida por massa evaporada:

- Líquidos puros: L = ΔvapH / M.
- Mistura, primário: L_vapor, média de L_i ponderada pela fração mássica de cada
  componente no vapor (composição do vapor por Raoult).
- Mistura, alternativo: média ponderada pela fração mássica do líquido (0,70 e 0,30).
  Usado como sensibilidade, para mostrar a faixa de incerteza do L da mistura.

Incertezas de L para o intervalo de confiança de L·r (fração relativa, NIST): água 0;
etanol 0,4/42,3 ≈ 0,9 %; isopropanol 3/45 ≈ 6,7 %; mistura: a incerteza do etanol
(0,9 %). A diferença entre os dois L da mistura NÃO entra no IC: é uma faixa de
sensibilidade do modelo (composição do vapor vs. do líquido), reportada à parte.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import stats

R_GAS_J_MOL_K: float = 8.314462618
T_REFERENCIA_K: float = 298.15
P_PADRAO_KPA: float = 100.0  # 1 bar, estado padrão JANAF

M_AGUA_G_MOL: float = 18.015
M_ETANOL_G_MOL: float = 46.068
M_ISOPROPANOL_G_MOL: float = 60.095

DVAP_AGUA_KJ_MOL: float = 44.00
DVAP_ETANOL_KJ_MOL: float = 42.3
DVAP_ETANOL_INCERTEZA_KJ_MOL: float = 0.4
DVAP_ISOPROPANOL_KJ_MOL: float = 45.0
DVAP_ISOPROPANOL_INCERTEZA_KJ_MOL: float = 3.0

# Antoine NIST: log10(P/bar) = A − B/(T + C), T em K.
ANTOINE_ETANOL = (5.24677, 1598.673, -46.424)
ANTOINE_ISOPROPANOL = (4.8610, 1357.427, -75.814)

# ΔfG°(g) e ΔfG°(l) de JANAF, em kJ/mol, a 298,15 K.
JANAF_DFG_AGUA_GAS_KJ_MOL: float = -228.582
JANAF_DFG_AGUA_LIQ_KJ_MOL: float = -237.141

FRACAO_MASSICA_ETANOL_MISTURA: float = 0.70
LIQUIDOS_CONHECIDOS: tuple[str, ...] = ("agua", "alcool 70%", "alcool 99%")


def pressao_vapor_agua_kpa(t_k: float = T_REFERENCIA_K) -> float:
    """Pressão de vapor da água a partir de ΔG de vaporização (JANAF). Válida a 298,15 K."""
    if t_k != T_REFERENCIA_K:
        raise ValueError("pressão da água calibrada somente em 298,15 K (JANAF)")
    delta_g_kj = JANAF_DFG_AGUA_GAS_KJ_MOL - JANAF_DFG_AGUA_LIQ_KJ_MOL
    return P_PADRAO_KPA * math.exp(-delta_g_kj * 1000.0 / (R_GAS_J_MOL_K * t_k))


def pressao_vapor_antoine_kpa(parametros: tuple[float, float, float], t_k: float) -> float:
    """Pressão de vapor (kPa) pela equação de Antoine NIST, P em bar."""
    a, b, c = parametros
    return 100.0 * 10.0 ** (a - b / (t_k + c))


def l_puro_kj_kg(dvap_kj_mol: float, massa_molar_g_mol: float) -> float:
    """Calor latente de vaporização por massa, em kJ/kg."""
    return dvap_kj_mol / massa_molar_g_mol * 1000.0


def composicao_mistura_etanol(fracao_massica_etanol: float) -> float:
    """Fração molar de etanol no líquido, a partir da fração mássica."""
    n_e = fracao_massica_etanol / M_ETANOL_G_MOL
    n_w = (1.0 - fracao_massica_etanol) / M_AGUA_G_MOL
    return n_e / (n_e + n_w)


def l_mistura_kj_kg(
    fracao_massica_etanol: float = FRACAO_MASSICA_ETANOL_MISTURA,
) -> dict[str, float]:
    """Calor latente efetivo da mistura etanol–água (primário e alternativo), em kJ/kg.

    Primário: fração mássica do vapor (Raoult ideal, composição inicial).
    Alternativo: fração mássica do líquido.
    """
    x_e = composicao_mistura_etanol(fracao_massica_etanol)
    x_w = 1.0 - x_e
    p_e = pressao_vapor_antoine_kpa(ANTOINE_ETANOL, T_REFERENCIA_K)
    p_w = pressao_vapor_agua_kpa()

    y_e = x_e * p_e / (x_e * p_e + x_w * p_w)
    y_w = 1.0 - y_e
    m_vapor = y_e * M_ETANOL_G_MOL + y_w * M_AGUA_G_MOL
    w_e_vapor = y_e * M_ETANOL_G_MOL / m_vapor
    w_w_vapor = 1.0 - w_e_vapor

    l_e = l_puro_kj_kg(DVAP_ETANOL_KJ_MOL, M_ETANOL_G_MOL)
    l_w = l_puro_kj_kg(DVAP_AGUA_KJ_MOL, M_AGUA_G_MOL)
    primario = w_e_vapor * l_e + w_w_vapor * l_w
    alternativo = fracao_massica_etanol * l_e + (1.0 - fracao_massica_etanol) * l_w
    return {
        "L_kj_kg": primario,
        "L_alternativo_kj_kg": alternativo,
        "fracao_molar_etanol_liquido": x_e,
        "fracao_molar_etanol_vapor": y_e,
        "fracao_massica_etanol_vapor": w_e_vapor,
        "pressao_etanol_kpa": p_e,
        "pressao_agua_kpa": p_w,
    }


def propriedades_liquido(nome: str) -> dict[str, float | str]:
    """Calor latente e incertezas relativas do líquido indicado em condicoes.csv.

    Levanta ValueError para um líquido desconhecido, com o nome recebido.
    """
    if nome == "agua":
        l = l_puro_kj_kg(DVAP_AGUA_KJ_MOL, M_AGUA_G_MOL)
        return {
            "liquido": nome, "descricao": "água", "L_kj_kg": l,
            "L_alternativo_kj_kg": l, "incerteza_L_relativa": 0.0,
        }
    if nome == "alcool 99%":
        l = l_puro_kj_kg(DVAP_ISOPROPANOL_KJ_MOL, M_ISOPROPANOL_G_MOL)
        return {
            "liquido": nome, "descricao": "isopropanol", "L_kj_kg": l,
            "L_alternativo_kj_kg": l,
            "incerteza_L_relativa": DVAP_ISOPROPANOL_INCERTEZA_KJ_MOL / DVAP_ISOPROPANOL_KJ_MOL,
        }
    if nome == "alcool 70%":
        m = l_mistura_kj_kg(FRACAO_MASSICA_ETANOL_MISTURA)
        return {
            "liquido": nome, "descricao": "etanol 70% (w/w)", "L_kj_kg": m["L_kj_kg"],
            "L_alternativo_kj_kg": m["L_alternativo_kj_kg"],
            "incerteza_L_relativa": DVAP_ETANOL_INCERTEZA_KJ_MOL / DVAP_ETANOL_KJ_MOL,
        }
    raise ValueError(f"líquido desconhecido em condicoes.csv: {nome!r}; esperado um de {LIQUIDOS_CONHECIDOS}")


def t_critico_95(graus_liberdade: float) -> float:
    """Quantil bilateral de 97,5 % da t de Student (IC95%). Requer graus_liberdade >= 1."""
    if not (graus_liberdade >= 1):
        raise ValueError("graus de liberdade devem ser >= 1")
    return float(stats.t.ppf(0.975, graus_liberdade))


def l_r_watts(l_kj_kg: float, taxa_g_s: float) -> float:
    """Produto L·r em W: (kJ/kg → J/kg) × (g/s → kg/s)."""
    return l_kj_kg * 1000.0 * taxa_g_s * 1e-3
