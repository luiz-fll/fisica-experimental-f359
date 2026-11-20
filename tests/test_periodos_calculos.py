"""Testes de ciclos, interpolação, estatísticas e agregação por janela (final/periodos.py)."""

import numpy as np
import pandas as pd
import pytest

from final.periodos import (
    COLUNAS_CICLOS,
    construir_ciclos,
    definir_limites_janelas,
    estatisticas_periodos,
    interpolar_massa,
    periodos_por_janela,
)


def massa_linear(t_max: float = 50.0) -> pd.DataFrame:
    """Massa m(t) = 41 - 0.01 t, leituras a cada 5 s, de 0 a ``t_max``."""
    tempos = np.arange(0.0, t_max + 1e-9, 5.0)
    return pd.DataFrame({"tempo_seg": tempos, "massa_g": 41.0 - 0.01 * tempos})


def mergulhos(*tempos: float) -> pd.DataFrame:
    return pd.DataFrame({"tempo_seg": list(tempos), "angulo_deg": [10.0] * len(tempos)})


# ---------------------------------------------------------------------------
# Interpolação
# ---------------------------------------------------------------------------


def test_interpolacao_exata_nos_nos_e_no_meio():
    tm = np.array([0.0, 10.0, 20.0])
    mm = np.array([41.0, 40.9, 40.7])
    resultado = interpolar_massa(tm, mm, np.array([0.0, 5.0, 10.0, 15.0, 20.0]))
    assert resultado == pytest.approx([41.0, 40.95, 40.9, 40.8, 40.7])


def test_interpolacao_nao_extrapola_fora_do_dominio():
    tm = np.array([10.0, 20.0, 30.0])
    mm = np.array([41.0, 40.9, 40.8])
    resultado = interpolar_massa(tm, mm, np.array([5.0, 35.0, 10.0, 30.0]))
    # np.interp repetiria o valor da borda em 5 e 35; a máscara deve deixá-los ausentes.
    assert np.isnan(resultado[0]) and np.isnan(resultado[1])
    assert resultado[2:] == pytest.approx([41.0, 40.8])


def test_interpolacao_com_consulta_nao_finita_retorna_nan():
    tm = np.array([0.0, 10.0])
    mm = np.array([41.0, 40.9])
    resultado = interpolar_massa(tm, mm, np.array([np.nan, np.inf, 5.0]))
    assert np.isnan(resultado[0]) and np.isnan(resultado[1])
    assert resultado[2] == pytest.approx(40.95)


def test_interpolacao_consulta_vazia():
    assert interpolar_massa(np.array([0.0, 1.0]), np.array([1.0, 2.0]), np.array([])).size == 0


@pytest.mark.parametrize(
    "tm,mm",
    [
        (np.array([]), np.array([])),
        (np.array([0.0, 0.0]), np.array([1.0, 2.0])),
        (np.array([10.0, 5.0]), np.array([1.0, 2.0])),
        (np.array([0.0, 1.0]), np.array([1.0])),
        (np.array([0.0, 1.0]), np.array([1.0, np.nan])),
    ],
)
def test_interpolacao_rejeita_massa_invalida(tm, mm):
    with pytest.raises(ValueError):
        interpolar_massa(tm, mm, np.array([0.5]))


# ---------------------------------------------------------------------------
# Ciclos
# ---------------------------------------------------------------------------


def test_ciclos_de_tres_mergulhos_com_periodo_e_ponto_medio():
    ciclos = construir_ciclos(mergulhos(2.0, 8.0, 14.0), massa_linear())
    assert list(ciclos.columns) == list(COLUNAS_CICLOS)
    assert ciclos["periodo_s"].tolist() == pytest.approx([6.0, 6.0])
    assert ciclos["ponto_medio_s"].tolist() == pytest.approx([5.0, 11.0])
    assert ciclos["t_inicial_s"].tolist() == [2.0, 8.0]
    assert ciclos["t_final_s"].tolist() == [8.0, 14.0]


def test_identificadores_de_evento_sao_posicoes_derivadas():
    ciclos = construir_ciclos(mergulhos(2.0, 8.0, 14.0), massa_linear())
    assert ciclos["evento_inicial"].tolist() == [1, 2]
    assert ciclos["evento_final"].tolist() == [2, 3]


def test_massa_no_ponto_medio_interpolada_linearmente():
    ciclos = construir_ciclos(mergulhos(2.0, 8.0, 14.0), massa_linear())
    # m(5) = 40.95 e m(11) = 40.89, pela reta m(t) = 41 - 0.01 t.
    assert ciclos["massa_ponto_medio_g"].tolist() == pytest.approx([40.95, 40.89])
    assert ciclos["suporte_massa"].tolist() == [True, True]


def test_ciclo_fora_do_dominio_da_massa_fica_sem_suporte():
    # Ponto médio de (60, 70) é 65 s, depois da última leitura de massa (50 s).
    ciclos = construir_ciclos(mergulhos(2.0, 8.0, 60.0, 70.0), massa_linear())
    assert ciclos["suporte_massa"].tolist() == [True, True, False]
    assert np.isnan(ciclos["massa_ponto_medio_g"].iloc[2])
    assert ciclos["periodo_s"].iloc[2] == pytest.approx(10.0)


def test_menos_de_dois_mergulhos_gera_tabela_vazia_com_colunas():
    ciclos = construir_ciclos(mergulhos(8.0), massa_linear())
    assert len(ciclos) == 0
    assert list(ciclos.columns) == list(COLUNAS_CICLOS)


def test_mergulhos_duplicados_sao_rejeitados():
    with pytest.raises(ValueError):
        construir_ciclos(mergulhos(2.0, 2.0, 8.0), massa_linear())


def test_mergulhos_desordenados_sao_rejeitados():
    with pytest.raises(ValueError):
        construir_ciclos(mergulhos(8.0, 2.0, 14.0), massa_linear())


def test_mergulho_nao_finito_e_rejeitado():
    with pytest.raises(ValueError):
        construir_ciclos(mergulhos(2.0, np.nan, 14.0), massa_linear())


def test_construir_ciclos_nao_altera_entradas():
    mg = mergulhos(2.0, 8.0, 14.0)
    ms = massa_linear()
    mg_antes, ms_antes = mg.copy(), ms.copy()
    construir_ciclos(mg, ms)
    pd.testing.assert_frame_equal(mg, mg_antes)
    pd.testing.assert_frame_equal(ms, ms_antes)


# ---------------------------------------------------------------------------
# Estatísticas
# ---------------------------------------------------------------------------


def test_estatisticas_com_tres_periodos_usam_desvio_amostral():
    estat = estatisticas_periodos(np.array([6.0, 6.0, 66.0]))
    assert estat["n"] == 3
    assert estat["media_s"] == pytest.approx(26.0)
    assert estat["desvio_padrao_s"] == pytest.approx(np.std([6.0, 6.0, 66.0], ddof=1))
    assert estat["minimo_s"] == 6.0
    assert estat["maximo_s"] == 66.0


def test_estatisticas_com_dois_periodos_calculam_desvio():
    estat = estatisticas_periodos(np.array([10.0, 14.0]))
    assert estat["desvio_padrao_s"] == pytest.approx(np.sqrt(8.0))


def test_estatisticas_com_um_periodo_nao_inventam_desvio():
    estat = estatisticas_periodos(np.array([12.0]))
    assert estat["n"] == 1
    assert estat["media_s"] == 12.0
    assert np.isnan(estat["desvio_padrao_s"])


def test_estatisticas_sem_periodos():
    estat = estatisticas_periodos(np.array([]))
    assert estat["n"] == 0
    assert all(np.isnan(estat[k]) for k in ("media_s", "desvio_padrao_s", "minimo_s", "maximo_s"))


def test_estatisticas_ignoram_valores_nao_finitos():
    estat = estatisticas_periodos(np.array([10.0, np.nan, 14.0]))
    assert estat["n"] == 2
    assert estat["media_s"] == pytest.approx(12.0)


# ---------------------------------------------------------------------------
# Agregação por janela
# ---------------------------------------------------------------------------


def ciclos_com_pontos_medios(*pontos: float) -> pd.DataFrame:
    """Ciclos sintéticos de período 6 s com os pontos médios dados."""
    return pd.DataFrame(
        {
            "ponto_medio_s": list(pontos),
            "periodo_s": [6.0] * len(pontos),
        }
    )


def test_ciclo_no_limite_entre_janelas_vai_para_a_seguinte():
    limites = definir_limites_janelas(600.0)
    tabela = periodos_por_janela(ciclos_com_pontos_medios(199.0, 200.0, 450.0), limites)
    assert tabela["n_ciclos"].tolist() == [1, 1, 1]


def test_janelas_sem_ciclos_e_com_um_ciclo_tem_status_explicito():
    limites = definir_limites_janelas(600.0)
    tabela = periodos_por_janela(ciclos_com_pontos_medios(10.0, 20.0, 450.0), limites)
    assert tabela["status"].tolist() == ["ok", "sem_ciclos", "sem_desvio"]
    assert tabela["n_ciclos"].tolist() == [2, 0, 1]
    assert np.isnan(tabela["desvio_padrao_s"].iloc[1])
    assert np.isnan(tabela["desvio_padrao_s"].iloc[2])


def test_todas_as_janelas_aparecem_mesmo_sem_ciclos():
    limites = definir_limites_janelas(600.0)
    tabela = periodos_por_janela(pd.DataFrame({"ponto_medio_s": [], "periodo_s": []}), limites)
    assert tabela["janela"].tolist() == [1, 2, 3]
    assert tabela["status"].tolist() == ["sem_ciclos"] * 3


def test_ciclo_com_ponto_medio_fora_das_janelas_nao_e_contado():
    limites = definir_limites_janelas(600.0)
    tabela = periodos_por_janela(ciclos_com_pontos_medios(10.0, 700.0), limites)
    assert tabela["n_ciclos"].sum() == 1


def test_estatisticas_por_janela_correspondem_ao_calculo_direto():
    limites = definir_limites_janelas(600.0)
    ciclos = pd.DataFrame(
        {"ponto_medio_s": [10.0, 30.0, 50.0], "periodo_s": [10.0, 14.0, 18.0]}
    )
    tabela = periodos_por_janela(ciclos, limites)
    linha = tabela.iloc[0]
    assert linha["media_s"] == pytest.approx(14.0)
    assert linha["desvio_padrao_s"] == pytest.approx(np.std([10.0, 14.0, 18.0], ddof=1))
    assert linha["status"] == "ok"
