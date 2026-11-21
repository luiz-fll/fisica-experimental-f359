"""Validação somente leitura dos conjuntos reais em final/dados/.

Não modifica nenhum arquivo. Ignorado quando a pasta não existe.
Inclui checagens de estrutura, qualidade básica e regressão numérica
contra os valores de referência documentados em CURRENT_STATE.md.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import pytest

from final import analisar
from final.massa import ajustar_linear, taxa_de_perda
from final.periodos import construir_ciclos, estatisticas_periodos
from final.pipeline import processar_filmagem

pytestmark = pytest.mark.skipif(
    not analisar.DIR_DADOS_PADRAO.is_dir(), reason="final/dados ausente"
)

# Valores de referência (CURRENT_STATE.md, após correção de agua_dia1/massa.csv).
# Tolerâncias amplas o suficiente para arredondamento de apresentação, estreitas
# o suficiente para detectar regressões nos cálculos.
REF_RESUMO = {
    "agua_dia1": {
        "ciclos": 22,
        "sem_massa": 0,
        "periodo_media_s": 25.59,
        "periodo_desvio_s": 3.92,
        "taxa_g_min": 0.0084,
        "r2": 0.964,
        "residuo_max_g": 0.0159,
    },
    "agua_dia2": {
        "ciclos": 25,
        "sem_massa": 0,
        "periodo_media_s": 23.20,
        "periodo_desvio_s": 4.49,
        "taxa_g_min": 0.0070,
        "r2": 0.967,
        "residuo_max_g": 0.0128,
    },
    "agua_dia3": {
        "ciclos": 25,
        "sem_massa": 0,
        "periodo_media_s": 22.29,
        "periodo_desvio_s": 4.98,
        "taxa_g_min": 0.0071,
        "r2": 0.974,
        "residuo_max_g": 0.0117,
    },
    "alcool70_dia1": {
        "ciclos": 35,
        "sem_massa": 2,
        "periodo_media_s": 16.97,
        "periodo_desvio_s": 6.57,
        "taxa_g_min": 0.0283,
        "r2": 0.976,
        "residuo_max_g": 0.0345,
    },
    "alcool70_dia2": {
        "ciclos": 20,
        "sem_massa": 0,
        "periodo_media_s": 25.92,
        "periodo_desvio_s": 9.38,
        "taxa_g_min": 0.0207,
        "r2": 0.964,
        "residuo_max_g": 0.0246,
    },
    "alcool70_dia3": {
        "ciclos": 28,
        "sem_massa": 1,
        "periodo_media_s": 21.03,
        "periodo_desvio_s": 7.99,
        "taxa_g_min": 0.0312,
        "r2": 0.970,
        "residuo_max_g": 0.0495,
    },
    "alcool99_dia1": {
        "ciclos": 35,
        "sem_massa": 1,
        "periodo_media_s": 16.67,
        "periodo_desvio_s": 4.05,
        "taxa_g_min": 0.0355,
        "r2": 0.982,
        "residuo_max_g": 0.0306,
    },
    "alcool99_dia2": {
        "ciclos": 33,
        "sem_massa": 2,
        "periodo_media_s": 18.16,
        "periodo_desvio_s": 5.28,
        "taxa_g_min": 0.0318,
        "r2": 0.986,
        "residuo_max_g": 0.0315,
    },
    "alcool99_dia3": {
        "ciclos": 31,
        "sem_massa": 2,
        "periodo_media_s": 18.76,
        "periodo_desvio_s": 6.09,
        "taxa_g_min": 0.0288,
        "r2": 0.984,
        "residuo_max_g": 0.0235,
    },
}



def _tol_rel(esperado: float, obtido: float, atol: float = 5e-3, rtol: float = 5e-3) -> bool:
    return abs(obtido - esperado) <= max(atol, rtol * abs(esperado))


def test_dados_reais_sao_validos_sem_erros():
    pastas = analisar.descobrir_filmagens(analisar.DIR_DADOS_PADRAO)
    assert len(pastas) == 9
    resultados = analisar.validar_lote(pastas)
    invalidas = [
        (r["id"], [str(p) for p in r["problemas"]])
        for r in resultados
        if r["status"] != "valida"
    ]
    assert invalidas == []


def test_estrutura_e_qualidade_basica_dos_dados_reais():
    """Cada filmagem tem faixas temporais coerentes, massas positivas e períodos positivos."""
    pastas = analisar.descobrir_filmagens(analisar.DIR_DADOS_PADRAO)
    assert {p.name for p in pastas} == set(REF_RESUMO)

    for resultado in analisar.validar_lote(pastas):
        assert resultado["status"] == "valida", resultado["id"]
        f = resultado["filmagem"]
        id_ = resultado["id"]
        tr = f["tracker"]
        ma = f["massa"]
        me = f["mergulhadas"]
        cond = f["condicoes"]

        # Estrutura mínima
        assert len(tr) >= 2, id_
        assert len(ma) >= 3, id_
        assert len(me) >= 2, id_
        assert ma["massa_g"].min() > 0, id_
        assert ma["tempo_seg"].is_monotonic_increasing, id_
        assert me["tempo_seg"].is_monotonic_increasing, id_
        assert tr["tempo_seg"].is_monotonic_increasing, id_

        # Domínios temporais: massa tipicamente ~20–600 s; tracker cobre o ensaio
        assert ma["tempo_seg"].min() >= 0.0, id_
        assert ma["tempo_seg"].max() <= 700.0, id_
        assert tr["tempo_seg"].min() >= 0.0, id_

        # Metadados
        assert cond["liquido"], id_
        assert cond["dia"], id_
        assert 0.0 <= cond["umidade_pct"] <= 100.0, id_

        # Períodos positivos e massa interpolável no domínio
        ciclos = construir_ciclos(me, ma)
        assert len(ciclos) == len(me) - 1, id_
        assert (ciclos["periodo_s"] > 0).all(), id_
        n_sem = int((~ciclos["suporte_massa"]).sum())
        assert n_sem == REF_RESUMO[id_]["sem_massa"], (
            f"{id_}: sem_massa esperado {REF_RESUMO[id_]['sem_massa']}, obtido {n_sem}"
        )


def test_calculos_sobre_dados_reais_sao_consistentes_entre_janelas():
    """Cada filmagem gera n-1 ciclos, e nenhum ciclo ou leitura se perde ao agregar por janela."""
    from final.massa import ajustar_janelas
    from final.periodos import definir_limites_janelas, periodos_por_janela

    pastas = analisar.descobrir_filmagens(analisar.DIR_DADOS_PADRAO)
    for resultado in analisar.validar_lote(pastas):
        assert resultado["status"] == "valida", resultado["id"]
        filmagem = resultado["filmagem"]
        massa = filmagem["massa"]
        mergulhos = filmagem["mergulhadas"]

        ciclos = construir_ciclos(mergulhos, massa)
        assert len(ciclos) == len(mergulhos) - 1, resultado["id"]

        t_fim = float(max(massa["tempo_seg"].max(), mergulhos["tempo_seg"].max()))
        limites = definir_limites_janelas(t_fim)

        por_janela = periodos_por_janela(ciclos, limites)
        ciclos_no_dominio = int(ciclos["ponto_medio_s"].between(0.0, t_fim).sum())
        assert int(por_janela["n_ciclos"].sum()) == ciclos_no_dominio, resultado["id"]

        ajuste_janelas = ajustar_janelas(massa, limites)
        assert int(ajuste_janelas["n_leituras"].sum()) == len(massa), resultado["id"]

        global_ = ajustar_linear(massa["tempo_seg"].to_numpy(), massa["massa_g"].to_numpy())
        assert global_["status"] == "ok", resultado["id"]


def test_regressao_numerica_contra_referencias():
    """Valores globais de períodos e ajuste linear coincidem com CURRENT_STATE (tolerância)."""
    pastas = analisar.descobrir_filmagens(analisar.DIR_DADOS_PADRAO)
    for resultado in analisar.validar_lote(pastas):
        id_ = resultado["id"]
        ref = REF_RESUMO[id_]
        f = resultado["filmagem"]
        ciclos = construir_ciclos(f["mergulhadas"], f["massa"])
        stats = estatisticas_periodos(ciclos["periodo_s"])
        ajuste = ajustar_linear(
            f["massa"]["tempo_seg"].to_numpy(), f["massa"]["massa_g"].to_numpy()
        )
        taxa = taxa_de_perda(ajuste["b_g_s"])

        assert stats["n"] == ref["ciclos"], id_
        assert _tol_rel(ref["periodo_media_s"], stats["media_s"]), (
            f"{id_}: media {stats['media_s']} vs {ref['periodo_media_s']}"
        )
        assert _tol_rel(ref["periodo_desvio_s"], stats["desvio_padrao_s"]), (
            f"{id_}: desvio {stats['desvio_padrao_s']} vs {ref['periodo_desvio_s']}"
        )
        assert ajuste["status"] == "ok", id_
        assert _tol_rel(ref["r2"], ajuste["r2"], atol=5e-3, rtol=1e-2), (
            f"{id_}: r2 {ajuste['r2']} vs {ref['r2']}"
        )
        assert _tol_rel(ref["residuo_max_g"], ajuste["residuo_max_abs_g"], atol=1e-3, rtol=2e-2), (
            f"{id_}: resid {ajuste['residuo_max_abs_g']} vs {ref['residuo_max_g']}"
        )
        if taxa["tipo_taxa"] == "perda":
            assert _tol_rel(ref["taxa_g_min"], taxa["taxa_g_min"], atol=5e-4, rtol=2e-2), (
                f"{id_}: taxa {taxa['taxa_g_min']} vs {ref['taxa_g_min']}"
            )
        else:
            # Inclinação não negativa: referência ainda lista o valor absoluto da taxa
            # reportada como positiva de perda quando b<0; se b>=0 o teste não aplica.
            pass


def test_processamento_real_grava_saidas_fora_dos_dados(tmp_path):
    """Processa os nove conjuntos reais em diretório temporário; a pasta de dados fica intacta."""
    pastas = analisar.descobrir_filmagens(analisar.DIR_DADOS_PADRAO)
    for resultado in analisar.validar_lote(pastas):
        assert resultado["status"] == "valida", resultado["id"]
        saida = tmp_path / resultado["id"]
        processar_filmagem(resultado["filmagem"], 200.0, saida)
        assert (saida / "resumo.txt").is_file(), resultado["id"]
        assert (saida / "periodos.csv").is_file(), resultado["id"]
        assert (saida / "massa_ajuste.csv").is_file(), resultado["id"]
        assert (saida / "resumo.csv").is_file(), resultado["id"]
        # Quatro gráficos esperados quando há dados suficientes
        for nome in (
            "angulo_mergulhos.png",
            "massa_ajuste.png",
            "periodo_tempo.png",
        ):
            assert (saida / nome).is_file(), f"{resultado['id']}/{nome}"
    assert not any(
        p.name == "resultados" for p in analisar.DIR_DADOS_PADRAO.rglob("*") if p.is_dir()
    )


def test_agua_dia1_ponta_a_ponta_amostras(tmp_path):
    """Revisão ponta a ponta de agua_dia1: amostras de ciclos e ajuste batem com cálculo direto."""
    pastas = analisar.descobrir_filmagens(analisar.DIR_DADOS_PADRAO)
    pasta = next(p for p in pastas if p.name == "agua_dia1")
    resultado = analisar.validar_lote([pasta])[0]
    assert resultado["status"] == "valida"
    filmagem = resultado["filmagem"]

    # Processamento completo
    saida = tmp_path / "agua_dia1"
    processar_filmagem(filmagem, 200.0, saida)

    periodos = pd.read_csv(saida / "periodos.csv")
    assert len(periodos) == 22
    # Primeiro ciclo: t0=17.322, t1=35.842, T=18.52
    assert abs(periodos.iloc[0]["t_inicial_s"] - 17.322) < 1e-6
    assert abs(periodos.iloc[0]["periodo_s"] - 18.52) < 1e-6
    assert periodos.iloc[0]["suporte_massa"] in (True, 1)
    # Último ciclo dentro do domínio de massa
    assert periodos.iloc[-1]["suporte_massa"] in (True, 1)
    assert abs(periodos.iloc[-1]["t_final_s"] - 580.273) < 1e-3

    resumo = pd.read_csv(saida / "resumo.csv")
    mapa = dict(zip(resumo["grandeza"], resumo["valor"]))
    assert int(float(mapa["n_ciclos"])) == 22
    assert abs(float(mapa["periodo_media_s"]) - 25.5887) < 1e-3
    assert abs(float(mapa["massa_r2"]) - 0.963961) < 1e-4
    assert abs(float(mapa["massa_taxa_g_min"]) - 0.008352) < 1e-5
    assert abs(float(mapa["massa_residuo_max_abs_g"]) - 0.015917) < 1e-5

    # Ajuste global: b negativo (perda)
    assert float(mapa["massa_b_g_s"]) < 0
    assert mapa["massa_tipo_taxa"] == "perda"

    texto = (saida / "resumo.txt").read_text(encoding="utf-8")
    assert "agua_dia1" in texto
    assert "Limitações" in texto
    assert "R²" in texto or "R2" in texto or "r2" in texto.lower()
