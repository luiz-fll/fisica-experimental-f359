"""Testes da convenção de janelas temporais (periodos.py)."""

import math

import numpy as np
import pandas as pd
import pytest

from final.periodos import atribuir_janela, definir_limites_janelas


def test_ensaio_de_600s_gera_tres_janelas_de_200s():
    limites = definir_limites_janelas(600.0)
    assert limites["janela"].tolist() == [1, 2, 3]
    assert limites["inicio_s"].tolist() == [0.0, 200.0, 400.0]
    assert limites["fim_s"].tolist() == [200.0, 400.0, 600.0]


def test_somente_a_ultima_janela_e_fechada_a_direita():
    limites = definir_limites_janelas(600.0)
    assert limites["fechada_direita"].tolist() == [False, False, True]


def test_instante_final_coincidente_com_limite_pertence_a_ultima_janela():
    limites = definir_limites_janelas(600.0)
    assert atribuir_janela([600.0], limites).tolist() == [3]


def test_tempo_alem_do_limite_e_absorvido_pela_ultima_janela():
    limites = definir_limites_janelas(610.0)
    assert limites["janela"].tolist() == [1, 2, 3]
    assert limites["inicio_s"].iloc[-1] == 400.0
    assert limites["fim_s"].iloc[-1] == 610.0
    assert limites["fechada_direita"].iloc[-1]


def test_ultima_janela_tem_entre_duracao_e_duracao_dobrada():
    for t_fim in [200.0, 250.0, 399.0, 600.007, 799.9]:
        limites = definir_limites_janelas(t_fim)
        tamanho = limites["fim_s"].iloc[-1] - limites["inicio_s"].iloc[-1]
        assert 200.0 <= tamanho < 400.0 or len(limites) == 1


def test_janelas_anteriores_mantem_duracao_fixa():
    limites = definir_limites_janelas(799.9)
    comprimentos = (limites["fim_s"] - limites["inicio_s"]).tolist()
    assert comprimentos[:-1] == [200.0] * (len(limites) - 1)


def test_ensaio_de_600_007s_absorve_o_resto_na_terceira_janela():
    # Caso real observado: última leitura de massa em 600,007 s.
    limites = definir_limites_janelas(600.007)
    assert len(limites) == 3
    assert limites["fim_s"].iloc[-1] == 600.007
    assert atribuir_janela([600.007], limites).tolist() == [3]


def test_t_fim_zero_gera_uma_janela_degenerada_de_origem():
    limites = definir_limites_janelas(0.0)
    assert len(limites) == 1
    assert limites["inicio_s"].iloc[0] == 0.0
    assert limites["fim_s"].iloc[0] == 0.0


def test_t_fim_exatamente_igual_a_duracao_gera_uma_janela():
    limites = definir_limites_janelas(200.0)
    assert len(limites) == 1
    assert limites["fim_s"].iloc[0] == 200.0


def test_t_fim_ligeiramente_acima_de_duracao_gera_uma_janela_absorvida():
    limites = definir_limites_janelas(200.1)
    assert len(limites) == 1
    assert limites["fim_s"].iloc[0] == 200.1


def test_t_fim_igual_a_multiplo_da_duracao_gera_janela_fechada_no_limite():
    limites = definir_limites_janelas(400.0)
    assert limites["fim_s"].tolist() == [200.0, 400.0]


def test_tolerancia_numerica_nao_cria_janela_extra():
    # Erro de ponto flutuante abaixo do limite não deve criar uma janela a mais.
    assert len(definir_limites_janelas(600.0 + 1e-12)) == 3


def test_tolerancia_numerica_nao_cria_janela_comecando_depois_de_t_fim():
    # 399,9999999999 está abaixo de 400: a segunda janela não pode começar em 400.
    limites = definir_limites_janelas(399.9999999999)
    assert (limites["inicio_s"] <= 399.9999999999).all()


def test_duracao_personalizada():
    limites = definir_limites_janelas(600.0, duracao=100.0)
    assert len(limites) == 6
    assert limites["fim_s"].iloc[-1] == 600.0


def test_duracao_personalizada_com_resto_absorvido():
    limites = definir_limites_janelas(650.0, duracao=100.0)
    assert len(limites) == 6
    assert limites["inicio_s"].iloc[-1] == 500.0
    assert limites["fim_s"].iloc[-1] == 650.0


@pytest.mark.parametrize("t_fim", [math.nan, math.inf, -1.0])
def test_t_fim_invalido_levanta_erro(t_fim):
    with pytest.raises(ValueError):
        definir_limites_janelas(t_fim)


@pytest.mark.parametrize("duracao", [0.0, -5.0, math.nan, math.inf])
def test_duracao_invalida_levanta_erro(duracao):
    with pytest.raises(ValueError):
        definir_limites_janelas(600.0, duracao=duracao)


def test_atribuicao_respeita_intervalos_semiabertos():
    limites = definir_limites_janelas(600.0)
    tempos = [0.0, 199.999, 200.0, 399.999, 400.0, 600.0]
    assert atribuir_janela(tempos, limites).tolist() == [1, 1, 2, 2, 3, 3]


def test_instantes_fora_do_dominio_recebem_na():
    limites = definir_limites_janelas(600.0)
    tempos = [-0.1, 600.001, np.nan, np.inf, -np.inf]
    resultado = atribuir_janela(tempos, limites)
    assert resultado.isna().all()
    assert str(resultado.dtype) == "Int64"


def test_atribuicao_preserva_tamanho_e_aceita_serie():
    limites = definir_limites_janelas(600.0)
    entrada = pd.Series([10.0, 250.0, 500.0], index=["a", "b", "c"])
    resultado = atribuir_janela(entrada, limites)
    assert len(resultado) == 3
    assert resultado.tolist() == [1, 2, 3]


def test_atribuicao_de_entrada_vazia():
    limites = definir_limites_janelas(600.0)
    assert len(atribuir_janela(np.array([], dtype=float), limites)) == 0
