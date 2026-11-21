"""Testes de constantes NIST, calor latente efetivo, IC95% e L·r.

Valores esperados: calculados à mão a partir dos dados NIST (ver constantes.py) e,
quando indicado, por fórmula independente reescrita aqui.
"""

import math

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from final import constantes as c
from final.massa import ajustar_linear, ic95_taxa_g_min
from final.periodos import estatisticas_periodos
from final.pipeline import _lr_com_ic


# ---------------------------------------------------------------------------
# Constantes e calor latente
# ---------------------------------------------------------------------------


def test_calor_latente_puro_com_conta_manual():
    assert c.l_puro_kj_kg(44.00, 18.015) == pytest.approx(2442.41, abs=0.01)
    assert c.l_puro_kj_kg(42.3, 46.068) == pytest.approx(918.3, abs=0.1)
    assert c.l_puro_kj_kg(45.0, 60.095) == pytest.approx(748.8, abs=0.1)


def test_pressao_agua_derivada_de_delta_g_janaf():
    # ΔG_vap = −237,141 − (−228,582) = 8,559 kJ/mol; P = exp(−ΔG/RT) bar.
    esperado = 100.0 * math.exp(-8559.0 / (8.314462618 * 298.15))
    assert c.pressao_vapor_agua_kpa() == pytest.approx(esperado, rel=1e-12)
    assert 3.15 < c.pressao_vapor_agua_kpa() < 3.18  # NIST ≈ 3,17 kPa


def test_pressao_agua_so_em_298_15k():
    with pytest.raises(ValueError):
        c.pressao_vapor_agua_kpa(300.0)


def test_pressao_etanol_antoine_nist_a_25c():
    p = c.pressao_vapor_antoine_kpa(c.ANTOINE_ETANOL, 298.15)
    assert 7.85 < p < 7.90  # NIST ≈ 7,87 kPa


def test_composicao_molar_do_etanol_70_pct_massa():
    # 70 g etanol + 30 g água: n_e = 70/46,068; n_w = 30/18,015.
    n_e = 0.70 / 46.068
    n_w = 0.30 / 18.015
    assert c.composicao_mistura_etanol(0.70) == pytest.approx(n_e / (n_e + n_w), rel=1e-12)


def test_l_mistura_primario_reproduzido_por_formula_independente():
    x_e = c.composicao_mistura_etanol(0.70)
    p_e = c.pressao_vapor_antoine_kpa(c.ANTOINE_ETANOL, 298.15)
    p_w = c.pressao_vapor_agua_kpa()
    y_e = x_e * p_e / (x_e * p_e + (1 - x_e) * p_w)
    m_vap = y_e * 46.068 + (1 - y_e) * 18.015
    w_e = y_e * 46.068 / m_vap
    l_e = 42.3 / 46.068 * 1000
    l_w = 44.00 / 18.015 * 1000
    esperado = w_e * l_e + (1 - w_e) * l_w
    assert c.l_mistura_kj_kg(0.70)["L_kj_kg"] == pytest.approx(esperado, rel=1e-12)


def test_l_mistura_alternativo_e_media_ponderada_pelo_liquido():
    m = c.l_mistura_kj_kg(0.70)
    l_e = 42.3 / 46.068 * 1000
    l_w = 44.00 / 18.015 * 1000
    assert m["L_alternativo_kj_kg"] == pytest.approx(0.70 * l_e + 0.30 * l_w, rel=1e-12)


def test_mistura_vapor_mais_rico_em_etanol_que_liquido():
    m = c.l_mistura_kj_kg(0.70)
    assert m["fracao_molar_etanol_vapor"] > m["fracao_molar_etanol_liquido"]


def test_liquido_desconhecido_levanta_erro_com_o_nome():
    with pytest.raises(ValueError, match="vinho"):
        c.propriedades_liquido("vinho")


def test_propriedades_isopropanol_usam_incerteza_nist():
    p = c.propriedades_liquido("alcool 99%")
    assert p["descricao"] == "isopropanol"
    assert p["incerteza_L_relativa"] == pytest.approx(3.0 / 45.0)


def test_propriedades_agua_sem_incerteza_de_L():
    assert c.propriedades_liquido("agua")["incerteza_L_relativa"] == 0.0


def test_t_critico_95_coincide_com_scipy_e_rejeita_df_invalido():
    assert c.t_critico_95(8) == pytest.approx(stats.t.ppf(0.975, 8))
    assert c.t_critico_95(28) == pytest.approx(2.0484, abs=1e-4)
    with pytest.raises(ValueError):
        c.t_critico_95(0)


def test_l_r_unidades_kj_kg_e_g_s_para_w():
    # 1 kJ/kg × 1 g/s = 1000 J/kg × 0,001 kg/s = 1 W.
    assert c.l_r_watts(1.0, 1.0) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# IC de inclinação e de taxa
# ---------------------------------------------------------------------------


def _dados_com_ruido(n: int = 30, seed: int = 7):
    rng = np.random.default_rng(seed)
    t = np.arange(20.0, 20.0 + 20.0 * n, 20.0)
    m = 41.5 - 0.0004 * t + rng.normal(0, 0.005, n)
    return t, m


def test_ic_de_b_coincide_com_formula_t_manual():
    t, m = _dados_com_ruido()
    r = ajustar_linear(t, m)
    n = len(t)
    t_crit = stats.t.ppf(0.975, n - 2)
    meia = t_crit * r["erro_padrao_b_g_s"]
    assert r["ic95_b_g_s_inf"] == pytest.approx(r["b_g_s"] - meia, rel=1e-12)
    assert r["ic95_b_g_s_sup"] == pytest.approx(r["b_g_s"] + meia, rel=1e-12)


def test_ic_de_b_contem_o_valor_verdadeiro_neste_caso_controlado():
    t, m = _dados_com_ruido()
    r = ajustar_linear(t, m)
    assert r["ic95_b_g_s_inf"] < -0.0004 < r["ic95_b_g_s_sup"]


def test_ic_de_b_nan_com_dois_pontos():
    r = ajustar_linear(np.array([0.0, 10.0]), np.array([41.0, 40.9]), min_leituras=2)
    assert np.isnan(r["ic95_b_g_s_inf"]) and np.isnan(r["ic95_b_g_s_sup"])


def test_ic_taxa_inverte_limites_de_b():
    # taxa = −60·b; o limite inferior da taxa vem do superior de b.
    inf, sup = ic95_taxa_g_min(-0.0006, -0.0004, "perda")
    assert inf == pytest.approx(0.024)
    assert sup == pytest.approx(0.036)


def test_ic_taxa_vazio_sem_perda():
    inf, sup = ic95_taxa_g_min(0.0001, 0.0003, "inclinacao_nao_negativa")
    assert np.isnan(inf) and np.isnan(sup)


def test_ic_media_periodos_com_scipy():
    x = np.array([6.0, 6.0, 66.0])
    estat = estatisticas_periodos(x)
    inf, sup = stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=x.std(ddof=1) / np.sqrt(len(x)))
    assert estat["ic95_media_inf_s"] == pytest.approx(inf, rel=1e-12)
    assert estat["ic95_media_sup_s"] == pytest.approx(sup, rel=1e-12)


def test_ic_media_periodos_nan_com_um_periodo():
    estat = estatisticas_periodos(np.array([12.0]))
    assert np.isnan(estat["ic95_media_inf_s"])


# ---------------------------------------------------------------------------
# L·r com incerteza
# ---------------------------------------------------------------------------


def test_lr_com_ic_conta_manual():
    # Taxa 0,0084 g/min com IC [0,0078; 0,0090]: meia-largura relativa = 0,0006/0,0084.
    r = _lr_com_ic(0.0084 / 60.0, 0.0078, 0.0090, 2442.4, 0.0, 2442.4)
    assert r["L_r_W"] == pytest.approx(2442.4e3 * (0.0084 / 60.0) * 1e-3)
    meia = 0.0006 / 0.0084
    assert r["L_r_ic95_inf_W"] == pytest.approx(r["L_r_W"] * (1 - meia), rel=1e-3)
    assert r["L_r_ic95_sup_W"] == pytest.approx(r["L_r_W"] * (1 + meia), rel=1e-3)


def test_lr_com_ic_combina_incerteza_de_L_em_quadratura():
    sem_L = _lr_com_ic(0.0084 / 60.0, 0.0078, 0.0090, 750.0, 0.0, 750.0)
    com_L = _lr_com_ic(0.0084 / 60.0, 0.0078, 0.0090, 750.0, 0.04, 750.0)
    meia_taxa = 0.0006 / 0.0084
    meia_total = math.hypot(meia_taxa, 0.04)
    assert com_L["L_r_ic95_sup_W"] - com_L["L_r_W"] == pytest.approx(com_L["L_r_W"] * meia_total, rel=1e-9)
    assert com_L["L_r_ic95_sup_W"] - com_L["L_r_W"] > sem_L["L_r_ic95_sup_W"] - sem_L["L_r_W"]


def test_lr_nan_sem_taxa_positiva():
    r = _lr_com_ic(np.nan, np.nan, np.nan, 2442.4, 0.0, 2442.4)
    assert np.isnan(r["L_r_W"]) and np.isnan(r["L_r_ic95_inf_W"])
