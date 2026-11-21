"""Testes da comparação entre filmagens (final/comparacao.py).

Usa filmagens sintéticas processadas pelo pipeline real, em diretório temporário.
Nenhum dado de final/dados é lido.
"""

import numpy as np
import pandas as pd
import pytest

from final.comparacao import gerar_comparacao
from final.pipeline import processar_filmagem


def filmagem(pasta, liquido, dia, periodo, taxa_min):
    """Filmagem sintética com período fixo e taxa de perda fixa (g/min)."""
    t_massa = np.arange(0.0, 600.0 + 1e-9, 20.0)
    b = -taxa_min / 60.0
    m = 41.5 + b * t_massa + np.array([0.001, -0.001] * (len(t_massa) // 2 + 1))[: len(t_massa)] * 0.5
    massa = pd.DataFrame({"tempo_seg": t_massa, "massa_g": m})
    eventos = np.arange(10.0, 590.0, periodo)
    merg = pd.DataFrame({"tempo_seg": eventos, "angulo_deg": 10.0})
    tracker = pd.DataFrame({"tempo_seg": np.arange(0, 601, 0.5), "angulo_deg": 10.0})
    return {
        "id": f"{liquido.replace(' ', '_').replace('%', 'pct')}_{dia}",
        "pasta": pasta,
        "tracker": tracker,
        "massa": massa,
        "mergulhadas": merg,
        "condicoes": {"liquido": liquido, "dia": dia, "temperatura_c": 23.9, "umidade_pct": 61.0},
        "avisos": [],
    }


def processar_lote(tmp_path, especificacoes):
    itens = []
    for f in especificacoes:
        f = dict(f)
        pasta_dados = tmp_path / "dados" / f["id"]
        pasta_dados.mkdir(parents=True, exist_ok=True)
        f["pasta"] = pasta_dados
        resultado = processar_filmagem(f, 200.0, tmp_path / "res" / f["id"])
        itens.append({
            "id": f["id"],
            "tabelas": resultado["tabelas"],
            "condicoes": f["condicoes"],
            "massa_df": resultado["massa_df"],
        })
    return itens


def especificacoes_dia(dia, periodos, taxas):
    """Três líquidos no mesmo dia: 'agua', 'alcool 70%', 'alcool 99%'."""
    liquidos = ["agua", "alcool 70%", "alcool 99%"]
    return [
        filmagem(None, liq, dia, per, taxa)
        for liq, per, taxa in zip(liquidos, periodos, taxas)
    ]


def test_arquivos_por_dia_e_entre_dias_sao_gravados(tmp_path):
    especs = especificacoes_dia("2026-10-19", (25.0, 17.0, 16.0), (0.008, 0.028, 0.035))
    especs += especificacoes_dia("2026-10-26", (23.0, 26.0, 18.0), (0.007, 0.021, 0.032))
    itens = processar_lote(tmp_path, especs)
    gerados = gerar_comparacao(itens, tmp_path / "res")
    pasta = tmp_path / "res" / "comparacao"
    for dia in ("2026-10-19", "2026-10-26"):
        for nome in ("comparacao_dia.csv", "hipoteses_dia.csv", "grafico_massa.png",
                     "grafico_periodos.png", "grafico_tau_vs_lr.png", "grafico_taxas_janelas.png"):
            assert (pasta / "por_dia" / dia / nome).is_file(), (dia, nome)
    assert (pasta / "entre_dias" / "variacao_por_liquido.csv").is_file()
    assert (pasta / "entre_dias" / "grafico_entre_dias.png").is_file()
    assert (pasta / "entre_dias" / "pares_janela.csv").is_file()
    assert (pasta / "leia_me.txt").is_file()
    assert len(gerados) >= 10


def test_comparacao_dia_agrupa_apenas_um_dia(tmp_path):
    especs = especificacoes_dia("2026-10-19", (25.0, 17.0, 16.0), (0.008, 0.028, 0.035))
    especs += especificacoes_dia("2026-10-26", (23.0, 26.0, 18.0), (0.007, 0.021, 0.032))
    gerar_comparacao(processar_lote(tmp_path, especs), tmp_path / "res")
    comp = pd.read_csv(tmp_path / "res" / "comparacao" / "por_dia" / "2026-10-19" / "comparacao_dia.csv")
    assert len(comp) == 3
    assert set(comp["dia"]) == {"2026-10-19"}
    assert set(comp["liquido"]) == {"agua", "alcool 70%", "alcool 99%"}


def test_hipotese_h2_descritiva_coincide_quando_ordem_de_periodo_coincide(tmp_path):
    # τ: alcool 99% (16) < alcool 70% (17) < agua (25): coincide com H2 do relatório.
    especs = especificacoes_dia("2026-10-19", (25.0, 17.0, 16.0), (0.008, 0.028, 0.035))
    gerar_comparacao(processar_lote(tmp_path, especs), tmp_path / "res")
    hip = pd.read_csv(tmp_path / "res" / "comparacao" / "por_dia" / "2026-10-19" / "hipoteses_dia.csv").iloc[0]
    assert hip["ordem_tau_observada_crescente"] == "alcool 99% < alcool 70% < agua"
    assert bool(hip["ordem_observada_coincide_com_H2_prevista"]) is True
    assert "descritivo" in hip["nota"].lower() or "Descritivo" in hip["nota"]


def test_h2_descritiva_detecta_discordancia(tmp_path):
    # agua com período menor que os álcoois: discorda da ordem prevista pela H2.
    especs = especificacoes_dia("2026-10-19", (12.0, 17.0, 25.0), (0.008, 0.028, 0.035))
    gerar_comparacao(processar_lote(tmp_path, especs), tmp_path / "res")
    hip = pd.read_csv(tmp_path / "res" / "comparacao" / "por_dia" / "2026-10-19" / "hipoteses_dia.csv").iloc[0]
    assert bool(hip["ordem_observada_coincide_com_H2_prevista"]) is False


def test_inclinacao_log_log_com_tres_pontos_e_calculada(tmp_path):
    especs = especificacoes_dia("2026-10-19", (25.0, 17.0, 16.0), (0.008, 0.028, 0.035))
    gerar_comparacao(processar_lote(tmp_path, especs), tmp_path / "res")
    hip = pd.read_csv(tmp_path / "res" / "comparacao" / "por_dia" / "2026-10-19" / "hipoteses_dia.csv").iloc[0]
    assert np.isfinite(hip["inclinacao_log_tau_vs_log_L_r"])
    assert hip["inclinacao_esperada_pelo_modelo"] == -1.0


def test_um_dia_com_dois_liquidos_nao_quebra(tmp_path):
    especs = especificacoes_dia("2026-10-19", (25.0, 17.0, 16.0), (0.008, 0.028, 0.035))[:2]
    gerados = gerar_comparacao(processar_lote(tmp_path, especs), tmp_path / "res")
    assert any(g.name == "comparacao_dia.csv" for g in gerados)
    comp = pd.read_csv(tmp_path / "res" / "comparacao" / "por_dia" / "2026-10-19" / "comparacao_dia.csv")
    assert len(comp) == 2


def test_lr_entre_dias_reflete_taxa_de_cada_dia(tmp_path):
    especs = especificacoes_dia("2026-10-19", (25.0, 17.0, 16.0), (0.008, 0.028, 0.035))
    especs += especificacoes_dia("2026-10-26", (23.0, 26.0, 18.0), (0.007, 0.021, 0.032))
    gerar_comparacao(processar_lote(tmp_path, especs), tmp_path / "res")
    var = pd.read_csv(tmp_path / "res" / "comparacao" / "entre_dias" / "variacao_por_liquido.csv")
    linha = var[(var["liquido"] == "alcool 99%") & (var["dia"] == "2026-10-26")].iloc[0]
    assert linha["taxa_g_min"] == pytest.approx(0.032, rel=0.05)
    assert linha["L_r_W"] > 0


def test_pares_janela_contem_L_r_por_janela(tmp_path):
    especs = especificacoes_dia("2026-10-19", (25.0, 17.0, 16.0), (0.008, 0.028, 0.035))
    gerar_comparacao(processar_lote(tmp_path, especs), tmp_path / "res")
    pares = pd.read_csv(tmp_path / "res" / "comparacao" / "entre_dias" / "pares_janela.csv")
    assert {"id", "liquido", "dia", "janela", "tau_media_s", "L_r_W"} <= set(pares.columns)
    assert len(pares) == 3 * 3  # três filmagens × três janelas


def test_lista_vazia_levanta_erro(tmp_path):
    with pytest.raises(ValueError):
        gerar_comparacao([], tmp_path)
