"""Testes de gráficos, relatório e pipeline (final/graficos.py, relatorio.py, pipeline.py).

Usam filmagens sintéticas em diretórios temporários. Nunca gravam em final/dados.
"""

import numpy as np
import pandas as pd
import pytest

from final import relatorio
from final.graficos import (
    DadosInsuficientes,
    plotar_angulo_mergulhos,
    plotar_massa_ajuste,
    plotar_periodo_massa,
    plotar_periodo_tempo,
)
from final.massa import ajustar_linear, taxa_de_perda
from final.periodos import construir_ciclos, definir_limites_janelas
from final.pipeline import processar_filmagem


def filmagem_sintetica(pasta, mergulhos=(2.0, 8.0, 14.0, 22.0), massa_t_max=50.0):
    """Filmagem em memória, no formato validado de analisar.carregar_filmagem."""
    t_tracker = np.arange(0.0, 30.0 + 1e-9, 0.5)
    tracker = pd.DataFrame({"tempo_seg": t_tracker, "angulo_deg": 10.0 + 5.0 * np.sin(t_tracker)})
    t_massa = np.arange(0.0, massa_t_max + 1e-9, 5.0)
    massa = pd.DataFrame({"tempo_seg": t_massa, "massa_g": 41.0 - 0.01 * t_massa})
    merg = pd.DataFrame(
        {"tempo_seg": list(mergulhos), "angulo_deg": [10.0 + 5.0 * np.sin(t) for t in mergulhos]}
    )
    return {
        "id": "sintetica",
        "pasta": pasta,
        "tracker": tracker,
        "massa": massa,
        "mergulhadas": merg,
        "condicoes": {"liquido": "agua", "dia": "2026-10-19", "temperatura_c": 23.4, "umidade_pct": 53.0},
        "avisos": [],
    }


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------


def test_figuras_sao_gravadas_como_png(tmp_path):
    f = filmagem_sintetica(tmp_path)
    limites = definir_limites_janelas(50.0)
    ciclos = construir_ciclos(f["mergulhadas"], f["massa"])
    ajuste = ajustar_linear(f["massa"]["tempo_seg"].to_numpy(), f["massa"]["massa_g"].to_numpy())
    for nome, chamada in [
        ("a.png", lambda c: plotar_angulo_mergulhos(f["tracker"], f["mergulhadas"], "x", c)),
        ("b.png", lambda c: plotar_massa_ajuste(f["massa"], ajuste, "x", c, limites)),
        ("c.png", lambda c: plotar_periodo_tempo(ciclos, "x", c, limites)),
        ("d.png", lambda c: plotar_periodo_massa(ciclos, "x", c)),
    ]:
        caminho = chamada(tmp_path / nome)
        assert caminho.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_angulo_sem_registros_suficientes_e_omitido():
    with pytest.raises(DadosInsuficientes, match="menos de 2"):
        plotar_angulo_mergulhos(pd.DataFrame({"tempo_seg": [1.0], "angulo_deg": [1.0]}),
                                pd.DataFrame({"tempo_seg": [], "angulo_deg": []}), "x", "/tmp/nao.png")


def test_massa_com_ajuste_sem_estimativa_e_omitida(tmp_path):
    # Três leituras no mesmo instante: há leituras suficientes, mas não há variação temporal.
    massa = pd.DataFrame({"tempo_seg": [5.0, 5.0, 5.0], "massa_g": [41.0, 40.9, 40.8]})
    ajuste = ajustar_linear(massa["tempo_seg"].to_numpy(), massa["massa_g"].to_numpy())
    with pytest.raises(DadosInsuficientes, match="sem estimativa"):
        plotar_massa_ajuste(massa, ajuste, "x", tmp_path / "m.png")
    assert not (tmp_path / "m.png").exists()


def test_massa_com_leituras_insuficientes_e_omitida(tmp_path):
    massa = pd.DataFrame({"tempo_seg": [0.0, 5.0], "massa_g": [41.0, 40.9]})
    ajuste = ajustar_linear(massa["tempo_seg"].to_numpy(), massa["massa_g"].to_numpy())
    with pytest.raises(DadosInsuficientes, match="mínimo 3"):
        plotar_massa_ajuste(massa, ajuste, "x", tmp_path / "m.png")


def test_periodo_tempo_com_um_ciclo_e_omitido(tmp_path):
    ciclos = construir_ciclos(pd.DataFrame({"tempo_seg": [2.0, 8.0]}), filmagem_sintetica(tmp_path)["massa"])
    with pytest.raises(DadosInsuficientes, match="1 ciclo"):
        plotar_periodo_tempo(ciclos, "x", tmp_path / "p.png")


def test_periodo_massa_sem_suporte_e_omitido(tmp_path):
    ciclos = construir_ciclos(pd.DataFrame({"tempo_seg": [60.0, 70.0, 80.0]}), filmagem_sintetica(tmp_path)["massa"])
    with pytest.raises(DadosInsuficientes, match="massa interpolada"):
        plotar_periodo_massa(ciclos, "x", tmp_path / "p.png")


def test_graficos_nao_alteram_os_dados(tmp_path):
    f = filmagem_sintetica(tmp_path)
    antes = f["massa"].copy()
    plotar_massa_ajuste(f["massa"], ajustar_linear(f["massa"]["tempo_seg"].to_numpy(), f["massa"]["massa_g"].to_numpy()), "x", tmp_path / "m.png")
    pd.testing.assert_frame_equal(f["massa"], antes)


# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------


def test_csv_preserva_precisao_completa(tmp_path):
    valor = 0.1 + 0.2  # 0.30000000000000004: não sobrevive a arredondamento de 6 casas
    tabela = pd.DataFrame({"x": [valor, 1.0 / 3.0]})
    relatorio.gravar_tabelas(tmp_path / "out", {"t.csv": tabela})
    # O arquivo guarda o valor completo; a leitura exata exige float_precision="round_trip".
    lido = pd.read_csv(tmp_path / "out" / "t.csv", float_precision="round_trip")
    assert lido["x"].tolist() == [valor, 1.0 / 3.0]


def test_valores_ausentes_viram_celulas_vazias(tmp_path):
    tabela = pd.DataFrame({"x": [1.0, np.nan], "y": [2.0, 3.0]})
    relatorio.gravar_tabelas(tmp_path / "out", {"t.csv": tabela})
    texto = (tmp_path / "out" / "t.csv").read_text(encoding="utf-8")
    assert texto.splitlines()[2] == ",3.0"
    assert pd.read_csv(tmp_path / "out" / "t.csv")["x"].isna().tolist() == [False, True]


def test_tabela_de_uma_coluna_marca_ausente_como_texto_vazio_lido_como_nan(tmp_path):
    # Em uma coluna só, o pandas grava "" para não gerar uma linha em branco; ambos são ausentes.
    relatorio.gravar_tabelas(tmp_path / "out", {"t.csv": pd.DataFrame({"x": [1.0, np.nan]})})
    assert pd.read_csv(tmp_path / "out" / "t.csv")["x"].isna().tolist() == [False, True]


def test_gravacao_dentro_da_pasta_de_origem_e_recusada(tmp_path):
    origem = tmp_path / "dados" / "f"
    origem.mkdir(parents=True)
    with pytest.raises(PermissionError):
        relatorio.gravar_tabelas(origem, {"t.csv": pd.DataFrame({"x": [1]})}, origem=origem)
    with pytest.raises(PermissionError):
        relatorio.gravar_resumo_texto(origem / "sub", "x", origem=origem)
    assert not (origem / "t.csv").exists()


def test_resumo_texto_declara_motivos_e_limitacoes():
    info = {
        "id": "f", "condicoes": {"liquido": "agua", "dia": "d", "temperatura_c": 23.4, "umidade_pct": 53.0},
        "t_fim_s": 600.0, "duracao_janela_s": 200.0, "n_janelas": 3, "n_mergulhos": 2,
        "periodos": {"n": 1, "media_s": 6.0, "desvio_padrao_s": np.nan, "minimo_s": 6.0, "maximo_s": 6.0},
        "n_ciclos_sem_suporte": 0,
        "massa": {"n_leituras": 3, "status": "ok", "b_g_s": -1e-4, "tipo_taxa": "perda", "taxa_g_s": 1e-4,
                  "taxa_g_min": 6e-3, "r2": 0.9, "erro_padrao_b_g_s": 1e-6, "residuo_max_abs_g": 0.01,
                  "diagnosticos": "poucos_pontos"},
        "avisos": ["mergulhadas.csv: aviso de teste"],
        "graficos": ["angulo_mergulhos.png"],
        "graficos_omitidos": [("periodo_tempo.png", "1 ciclo(s)")],
    }
    texto = relatorio.montar_resumo_texto(info)
    assert "Resumo da filmagem f" in texto
    assert "omitido: periodo_tempo.png — 1 ciclo(s)" in texto
    assert "desvio-padrão ausente" in texto
    assert "Não são uma verificação da hipótese" in texto
    assert "aviso de teste" in texto


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def test_pipeline_grava_todos_os_arquivos_derivados(tmp_path):
    origem = tmp_path / "dados" / "sintetica"
    origem.mkdir(parents=True)
    f = filmagem_sintetica(origem)
    resultado = processar_filmagem(f, 200.0, tmp_path / "res" / "sintetica")
    saida = tmp_path / "res" / "sintetica"
    nomes = {p.name for p in saida.iterdir()}
    assert {"periodos.csv", "massa_ajuste.csv", "massa_residuos.csv", "massa_por_janela.csv",
            "periodo_por_janela.csv", "resumo.csv", "resumo.txt"} <= nomes
    assert resultado["status"] == "processada"


def test_pipeline_periodos_e_ajuste_coincidem_com_calculo_direto(tmp_path):
    origem = tmp_path / "dados" / "sintetica"
    origem.mkdir(parents=True)
    f = filmagem_sintetica(origem)
    processar_filmagem(f, 200.0, tmp_path / "res" / "sintetica")
    periodos = pd.read_csv(tmp_path / "res" / "sintetica" / "periodos.csv")
    assert len(periodos) == len(f["mergulhadas"]) - 1
    assert periodos["periodo_s"].tolist() == pytest.approx([6.0, 6.0, 8.0])
    assert periodos["janela"].tolist() == [1, 1, 1]
    ajuste = pd.read_csv(tmp_path / "res" / "sintetica" / "massa_ajuste.csv")
    b_ref = taxa_de_perda(ajustar_linear(f["massa"]["tempo_seg"].to_numpy(), f["massa"]["massa_g"].to_numpy())["b_g_s"])
    assert ajuste["b_g_s"].iloc[0] == pytest.approx(b_ref["b_g_s"], rel=1e-12)
    assert ajuste["taxa_g_min"].iloc[0] == pytest.approx(b_ref["taxa_g_min"], rel=1e-12)


def test_pipeline_registra_graficos_omitidos_com_motivo(tmp_path):
    origem = tmp_path / "dados" / "sintetica"
    origem.mkdir(parents=True)
    f = filmagem_sintetica(origem, mergulhos=(60.0, 70.0))  # 1 ciclo, fora da massa
    resultado = processar_filmagem(f, 200.0, tmp_path / "res" / "sintetica")
    omitidos = dict(resultado["graficos_omitidos"])
    assert "periodo_tempo.png" in omitidos and "1 ciclo" in omitidos["periodo_tempo.png"]
    assert "periodo_massa_exploratorio.png" in omitidos
    texto = (tmp_path / "res" / "sintetica" / "resumo.txt").read_text(encoding="utf-8")
    assert "omitido: periodo_tempo.png" in texto


def test_pipeline_recusa_saida_dentro_dos_dados(tmp_path):
    origem = tmp_path / "dados" / "sintetica"
    origem.mkdir(parents=True)
    f = filmagem_sintetica(origem)
    with pytest.raises(PermissionError):
        processar_filmagem(f, 200.0, origem / "resultados")
    assert not (origem / "resultados").exists()


def test_pipeline_nao_le_arquivos_da_origem(tmp_path):
    """A origem não existe em disco: o pipeline deve usar apenas o dicionário recebido."""
    f = filmagem_sintetica(tmp_path / "inexistente")
    resultado = processar_filmagem(f, 200.0, tmp_path / "res" / "sintetica")
    assert resultado["status"] == "processada"


def test_pipeline_nao_altera_as_tabelas_de_entrada(tmp_path):
    origem = tmp_path / "dados" / "sintetica"
    origem.mkdir(parents=True)
    f = filmagem_sintetica(origem)
    antes = {k: f[k].copy() for k in ("tracker", "massa", "mergulhadas")}
    processar_filmagem(f, 200.0, tmp_path / "res" / "sintetica")
    for chave, tabela in antes.items():
        pd.testing.assert_frame_equal(f[chave], tabela)
