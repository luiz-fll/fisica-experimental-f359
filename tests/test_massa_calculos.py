"""Testes do ajuste linear, taxas e ajustes por janela (final/massa.py)."""

import numpy as np
import pandas as pd
import pytest

from final.massa import (
    COLUNAS_AJUSTE_JANELA,
    ajustar_janelas,
    ajustar_linear,
    taxa_de_perda,
)
from final.periodos import definir_limites_janelas


def ruido_fixo(n: int = 30) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(12345)
    t = np.linspace(0.0, 600.0, n)
    m = 41.5 - 0.0002 * t + rng.normal(0.0, 0.01, n)
    return t, m


# ---------------------------------------------------------------------------
# Ajuste linear
# ---------------------------------------------------------------------------


def test_reta_exata_e_recuperada():
    t = np.arange(0.0, 600.0, 20.0)
    m = 41.5 - 0.0003 * t
    r = ajustar_linear(t, m)
    assert r["a_g"] == pytest.approx(41.5)
    assert r["b_g_s"] == pytest.approx(-0.0003)
    assert r["r2"] == pytest.approx(1.0)
    assert np.max(np.abs(r["residuos_g"])) < 1e-12
    assert r["status"] == "ok"
    assert r["diagnosticos"] == []


def test_coeficientes_coincidem_com_polyfit_independente():
    t, m = ruido_fixo()
    r = ajustar_linear(t, m)
    b_ref, a_ref = np.polyfit(t, m, 1)
    assert r["b_g_s"] == pytest.approx(b_ref, rel=1e-10)
    assert r["a_g"] == pytest.approx(a_ref, rel=1e-10)


def test_erro_padrao_coincide_com_formula_matricial():
    t, m = ruido_fixo()
    r = ajustar_linear(t, m)
    X = np.column_stack([np.ones_like(t), t])
    coef, *_ = np.linalg.lstsq(X, m, rcond=None)
    s2 = np.sum((m - X @ coef) ** 2) / (len(t) - 2)
    erro_b = np.sqrt(s2 * np.linalg.inv(X.T @ X)[1, 1])
    assert r["erro_padrao_b_g_s"] == pytest.approx(erro_b, rel=1e-10)


def test_r2_coincide_com_quadrado_da_correlacao():
    t, m = ruido_fixo()
    r = ajustar_linear(t, m)
    assert r["r2"] == pytest.approx(np.corrcoef(t, m)[0, 1] ** 2, rel=1e-10)


def test_residuo_e_observado_menos_ajustado():
    t = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    m = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    m[2] += 0.5  # ponto acima da reta
    r = ajustar_linear(t, m)
    assert r["residuos_g"][2] > 0
    assert np.sum(r["residuos_g"]) == pytest.approx(0.0, abs=1e-12)


@pytest.mark.parametrize("n,esperado", [(3, ["poucos_pontos"]), (4, ["poucos_pontos"]), (5, [])])
def test_diagnostico_de_poucos_pontos(n, esperado):
    t = np.arange(float(n))
    m = 41.0 - 0.01 * t + np.where(np.arange(n) % 2 == 0, 0.001, -0.001)
    assert ajustar_linear(t, m)["diagnosticos"] == esperado


def test_leituras_insuficientes_nao_ajustam():
    r = ajustar_linear(np.array([0.0, 10.0]), np.array([41.0, 40.9]))
    assert r["status"] == "leituras_insuficientes"
    assert np.isnan(r["a_g"]) and np.isnan(r["b_g_s"]) and np.isnan(r["r2"])
    assert len(r["residuos_g"]) == 2 and np.all(np.isnan(r["residuos_g"]))


def test_min_leituras_pode_ser_reduzido_com_diagnostico():
    r = ajustar_linear(np.array([0.0, 10.0]), np.array([41.0, 40.9]), min_leituras=2)
    assert r["status"] == "ok"
    assert r["b_g_s"] == pytest.approx(-0.01)
    assert set(r["diagnosticos"]) == {"poucos_pontos", "sem_graus_de_liberdade"}


def test_dois_pontos_nao_inventam_erro_padrao():
    r = ajustar_linear(np.array([0.0, 10.0]), np.array([41.0, 40.9]), min_leituras=2)
    assert np.isnan(r["erro_padrao_b_g_s"])
    assert np.isnan(r["erro_padrao_residuos_g"])
    assert np.max(np.abs(r["residuos_g"])) < 1e-12


def test_tempos_identicos_nao_ajustam():
    r = ajustar_linear(np.array([5.0, 5.0, 5.0]), np.array([41.0, 40.9, 40.8]))
    assert r["status"] == "sem_variacao_temporal"
    assert np.isnan(r["b_g_s"])


def test_massa_constante_tem_r2_indefinido():
    t = np.arange(6.0)
    r = ajustar_linear(t, np.full(6, 41.0))
    assert r["b_g_s"] == pytest.approx(0.0, abs=1e-12)
    assert np.isnan(r["r2"])
    assert "massa_constante" in r["diagnosticos"]


@pytest.mark.parametrize(
    "t,m,min_l",
    [
        (np.array([0.0, 1.0]), np.array([1.0]), 3),
        (np.array([0.0, np.nan, 2.0]), np.array([1.0, 2.0, 3.0]), 3),
        (np.array([0.0, 1.0, 2.0]), np.array([1.0, 2.0, np.inf]), 3),
        (np.array([0.0, 1.0, 2.0]), np.array([1.0, 2.0, 3.0]), 1),
    ],
)
def test_entradas_invalidas_levantam_erro(t, m, min_l):
    with pytest.raises(ValueError):
        ajustar_linear(t, m, min_leituras=min_l)


def test_ajuste_nao_altera_entradas():
    t, m = ruido_fixo()
    t0, m0 = t.copy(), m.copy()
    ajustar_linear(t, m)
    assert np.array_equal(t, t0) and np.array_equal(m, m0)


# ---------------------------------------------------------------------------
# Taxas
# ---------------------------------------------------------------------------


def test_taxa_positiva_de_perda_com_conversao_para_minuto():
    r = taxa_de_perda(-0.0003)
    assert r["tipo_taxa"] == "perda"
    assert r["taxa_g_s"] == pytest.approx(0.0003)
    assert r["taxa_g_min"] == pytest.approx(0.018)
    assert r["b_g_s"] == pytest.approx(-0.0003)


def test_inclinacao_positiva_nao_vira_taxa():
    r = taxa_de_perda(0.0002)
    assert r["tipo_taxa"] == "inclinacao_nao_negativa"
    assert np.isnan(r["taxa_g_s"]) and np.isnan(r["taxa_g_min"])
    assert r["b_g_s"] == pytest.approx(0.0002)


def test_inclinacao_zero_nao_vira_taxa():
    r = taxa_de_perda(0.0)
    assert r["tipo_taxa"] == "inclinacao_nao_negativa"
    assert np.isnan(r["taxa_g_s"])


def test_inclinacao_negativa_muito_pequena_preserva_sinal():
    r = taxa_de_perda(-1e-9)
    assert r["tipo_taxa"] == "perda"
    assert r["taxa_g_s"] == pytest.approx(1e-9)


def test_inclinacao_nao_finita_e_indefinida():
    r = taxa_de_perda(np.nan)
    assert r["tipo_taxa"] == "indefinido"
    assert np.isnan(r["b_g_s"]) and np.isnan(r["taxa_g_min"])


# ---------------------------------------------------------------------------
# Ajustes por janela
# ---------------------------------------------------------------------------


def massa_em_tres_janelas() -> pd.DataFrame:
    """Janela 1 e 2 com perda constante; janela 3 com ganho, para testar isolamento."""
    t = np.arange(0.0, 600.0 + 1e-9, 20.0)
    m = np.where(t < 400.0, 41.5 - 0.0002 * t, 41.5 - 0.0002 * 400.0 + 0.0001 * (t - 400.0))
    return pd.DataFrame({"tempo_seg": t, "massa_g": m})


def test_janelas_ajustam_separadamente_e_taxa_em_minuto():
    limites = definir_limites_janelas(600.0)
    tabela = ajustar_janelas(massa_em_tres_janelas(), limites)
    assert list(tabela.columns) == list(COLUNAS_AJUSTE_JANELA)
    assert tabela["janela"].tolist() == [1, 2, 3]
    assert tabela["b_g_s"].iloc[0] == pytest.approx(-0.0002)
    assert tabela["b_g_s"].iloc[1] == pytest.approx(-0.0002)
    assert tabela["taxa_g_min"].iloc[0] == pytest.approx(-60.0 * -0.0002)
    assert tabela["tipo_taxa"].tolist() == ["perda", "perda", "inclinacao_nao_negativa"]


def test_janela_com_ganho_nao_contamina_as_outras():
    limites = definir_limites_janelas(600.0)
    tabela = ajustar_janelas(massa_em_tres_janelas(), limites)
    assert tabela["b_g_s"].iloc[0] == pytest.approx(-0.0002)
    assert tabela["b_g_s"].iloc[2] > 0


def test_leitura_no_limite_entre_janelas_pertence_a_seguinte():
    limites = definir_limites_janelas(600.0)
    tabela = ajustar_janelas(massa_em_tres_janelas(), limites)
    # 400 s pertence à janela 3, que é [400, 600]; a janela 2 tem leituras até 380 s.
    assert tabela["n_leituras"].tolist() == [10, 10, 11]


def test_janela_com_leituras_insuficientes_fica_na_tabela():
    massa = pd.DataFrame({"tempo_seg": [0.0, 20.0, 40.0, 250.0, 260.0], "massa_g": [41.0, 40.9, 40.8, 40.7, 40.6]})
    limites = definir_limites_janelas(600.0)
    tabela = ajustar_janelas(massa, limites)
    assert tabela["status"].tolist() == ["ok", "leituras_insuficientes", "leituras_insuficientes"]
    assert tabela["n_leituras"].tolist() == [3, 2, 0]
    assert np.isnan(tabela["b_g_s"].iloc[1])


def test_janela_com_quatro_leituras_tem_diagnostico_de_poucos_pontos():
    massa = pd.DataFrame(
        {"tempo_seg": [0.0, 50.0, 100.0, 150.0], "massa_g": [41.0, 40.95, 40.9, 40.86]}
    )
    tabela = ajustar_janelas(massa, definir_limites_janelas(200.0))
    assert tabela["status"].iloc[0] == "ok"
    assert tabela["diagnosticos"].iloc[0] == "poucos_pontos"


def test_diagnosticos_vazios_viram_string_vazia():
    limites = definir_limites_janelas(600.0)
    tabela = ajustar_janelas(massa_em_tres_janelas(), limites)
    assert tabela["diagnosticos"].iloc[0] == ""


def test_ajuste_por_janela_nao_altera_a_massa():
    massa = massa_em_tres_janelas()
    antes = massa.copy()
    ajustar_janelas(massa, definir_limites_janelas(600.0))
    pd.testing.assert_frame_equal(massa, antes)
