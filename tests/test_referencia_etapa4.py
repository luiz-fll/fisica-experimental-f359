"""Referência independente para as grandezas da etapa 4 (L, IC, L·r) sobre os dados reais.

Recalcula, a partir dos CSVs e só com numpy/scipy, a taxa, o IC95% e o L·r de cada
filmagem, e compara com ``massa_ajuste.csv`` gerado pelo pipeline. Os valores de L são
escritos aqui à mão, a partir de NIST, para não reutilizar ``constantes.py``.
Dados reais em modo leitura; ignorado se final/dados não existir.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from final import analisar
from final.pipeline import processar_filmagem

L_KJ_KG = {  # NIST, calculado à mão: ΔvapH/M; mistura = vapor por Raoult a 25 °C
    "agua": 44.00 / 18.015 * 1000.0,
    "alcool 99%": 45.0 / 60.095 * 1000.0,
    "alcool 70%": None,  # conferido abaixo contra a fórmula independente
}
pytestmark = pytest.mark.skipif(not analisar.DIR_DADOS_PADRAO.is_dir(), reason="final/dados ausente")


def _L_mistura_independente() -> float:
    """Sem reutilizar constantes.py. Pressão da água deve ser ≈ 3,17 kPa (verificado abaixo)."""
    x_e = (0.70 / 46.068) / (0.70 / 46.068 + 0.30 / 18.015)
    p_e = 100 * 10 ** (5.24677 - 1598.673 / (298.15 - 46.424))
    dg_vap = -228.582 - (-237.141)  # ΔG_vap = ΔfG(gás) − ΔfG(líquido), kJ/mol (JANAF)
    p_w = 100 * np.exp(-dg_vap * 1000 / (8.314462618 * 298.15))  # kPa; ≈ 3,17 kPa
    assert 3.1 < p_w < 3.2, p_w  # sanidade física: água a 25 °C
    y_e = x_e * p_e / (x_e * p_e + (1 - x_e) * p_w)
    m_v = y_e * 46.068 + (1 - y_e) * 18.015
    w_e = y_e * 46.068 / m_v
    return w_e * (42.3 / 46.068 * 1000) + (1 - w_e) * (44.00 / 18.015 * 1000)


L_KJ_KG["alcool 70%"] = _L_mistura_independente()


def _referencia(pasta: Path) -> dict:
    cond = pd.read_csv(pasta / "condicoes.csv").iloc[0]
    m = pd.read_csv(pasta / "massa.csv")
    t = m["tempo_seg"].to_numpy(float)
    y = m["massa_g"].to_numpy(float)
    n = len(t)
    b, a = np.polyfit(t, y, 1)
    res = y - (a + b * t)
    se_res = np.sqrt(np.sum(res**2) / (n - 2))
    se_b = se_res / np.sqrt(np.sum((t - t.mean()) ** 2))
    t_crit = stats.t.ppf(0.975, n - 2)
    taxa = -60.0 * b
    ic = (-60.0 * (b + t_crit * se_b), -60.0 * (b - t_crit * se_b))
    l = L_KJ_KG[cond["liquido"]]
    lr = l * 1e3 * (-b) * 1e-3
    return {"liquido": cond["liquido"], "taxa": taxa, "ic": ic, "L": l, "lr": lr}


@pytest.fixture(scope="module")
def saidas(tmp_path_factory):
    base = tmp_path_factory.mktemp("ref_etapa4")
    out = {}
    for item in analisar.validar_lote(sorted(analisar.descobrir_filmagens(analisar.DIR_DADOS_PADRAO))):
        assert item["status"] == "valida", item["id"]
        processar_filmagem(item["filmagem"], 200.0, base / item["id"])
        out[item["id"]] = base / item["id"]
    return out


@pytest.mark.parametrize("pasta", sorted(analisar.descobrir_filmagens(analisar.DIR_DADOS_PADRAO))
                         if analisar.DIR_DADOS_PADRAO.is_dir() else [],
                         ids=lambda p: p.name)
def test_pipeline_coincide_com_referencia_para_taxa_IC_e_L_r(pasta, saidas):
    ref = _referencia(pasta)
    ajuste = pd.read_csv(saidas[pasta.name] / "massa_ajuste.csv", float_precision="round_trip").iloc[0]
    assert ajuste["liquido"] == ref["liquido"]
    assert ajuste["taxa_g_min"] == pytest.approx(ref["taxa"], rel=1e-9)
    assert ajuste["ic95_taxa_g_min_inf"] == pytest.approx(ref["ic"][0], rel=1e-9)
    assert ajuste["ic95_taxa_g_min_sup"] == pytest.approx(ref["ic"][1], rel=1e-9)
    assert ajuste["L_kj_kg"] == pytest.approx(ref["L"], rel=1e-9)
    assert ajuste["L_r_W"] == pytest.approx(ref["lr"], rel=1e-9)
