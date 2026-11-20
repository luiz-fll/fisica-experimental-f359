"""Orquestração do processamento de uma filmagem.

``processar_filmagem(filmagem, duracao_janela_s, pasta_saida)``

- ``filmagem`` é o dicionário validado produzido por ``analisar.carregar_filmagem``
  (chaves ``id``, ``pasta``, ``tracker``, ``massa``, ``mergulhadas``, ``condicoes``,
  ``avisos``). Não lê arquivos: a leitura é responsabilidade de ``analisar.py``.
- ``pasta_saida`` é a pasta de resultados *desta* filmagem (por exemplo
  ``final/resultados/agua_dia1``). Nunca pode estar dentro da pasta de dados.
- ``t_fim`` é o maior instante entre ``massa.csv`` e ``mergulhadas.csv``; define as
  janelas. Nenhuma janela é escolhida a partir dos resultados.

Retorna um dicionário com ``id``, ``status`` (``"processada"``), ``pasta_saida``,
``arquivos`` (CSVs gravados), ``graficos`` (PNGs gerados), ``graficos_omitidos``
(pares nome e motivo) e ``tabelas`` (DataFrames, para inspeção).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from final.graficos import (
    DadosInsuficientes,
    plotar_angulo_mergulhos,
    plotar_massa_ajuste,
    plotar_periodo_massa,
    plotar_periodo_tempo,
)
from final.massa import COLUNAS_AJUSTE_JANELA, ajustar_janelas, ajustar_linear, taxa_de_perda
from final.periodos import (
    COLUNAS_CICLOS,
    atribuir_janela,
    construir_ciclos,
    definir_limites_janelas,
    estatisticas_periodos,
    periodos_por_janela,
)
from final.relatorio import gravar_resumo_texto, gravar_tabelas, montar_resumo_texto

COLUNAS_AJUSTE_GLOBAL: tuple[str, ...] = (
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


def _verificar_saida_fora_dos_dados(pasta_saida: Path, origem: Path) -> None:
    saida = pasta_saida.resolve()
    dados = origem.resolve()
    if saida == dados or dados in saida.parents:
        raise PermissionError(f"pasta de saída dentro dos dados brutos: {pasta_saida}")


def _tabela_ciclos(ciclos: pd.DataFrame, limites: pd.DataFrame) -> pd.DataFrame:
    """Tabela de ciclos com a janela de cada ponto médio, em ordem fixa de colunas."""
    janela = atribuir_janela(ciclos["ponto_medio_s"], limites) if len(ciclos) else pd.Series(dtype="Int64")
    return ciclos.assign(janela=janela.astype("Int64").to_numpy())[[*COLUNAS_CICLOS, "janela"]]


def _tabela_ajuste_global(ajuste: dict, taxa: dict) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
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
        ],
        columns=list(COLUNAS_AJUSTE_GLOBAL),
    )


def _tabela_residuos(massa: pd.DataFrame, ajuste: dict) -> pd.DataFrame:
    ajustado = (
        ajuste["a_g"] + ajuste["b_g_s"] * massa["tempo_seg"].to_numpy(dtype=float)
        if ajuste["status"] == "ok"
        else np.full(len(massa), np.nan)
    )
    return pd.DataFrame(
        {
            "tempo_seg": massa["tempo_seg"].to_numpy(dtype=float),
            "massa_g": massa["massa_g"].to_numpy(dtype=float),
            "massa_ajustada_g": ajustado,
            "residuo_g": ajuste["residuos_g"],
        }
    )


def _tabela_resumo(info: dict) -> pd.DataFrame:
    """Resumo em formato longo (grandeza, valor, unidade), sem arredondamento."""
    cond = info["condicoes"]
    per = info["periodos"]
    mas = info["massa"]
    linhas = [
        ("id", info["id"], "texto"),
        ("liquido", cond["liquido"], "texto"),
        ("dia", cond["dia"], "texto"),
        ("temperatura_c", cond["temperatura_c"], "°C"),
        ("umidade_pct", cond["umidade_pct"], "%"),
        ("t_fim_s", info["t_fim_s"], "s"),
        ("duracao_janela_s", info["duracao_janela_s"], "s"),
        ("n_janelas", info["n_janelas"], "adimensional"),
        ("n_mergulhos", info["n_mergulhos"], "adimensional"),
        ("n_ciclos", per["n"], "adimensional"),
        ("n_ciclos_sem_suporte_massa", info["n_ciclos_sem_suporte"], "adimensional"),
        ("periodo_media_s", per["media_s"], "s"),
        ("periodo_desvio_padrao_s", per["desvio_padrao_s"], "s"),
        ("periodo_minimo_s", per["minimo_s"], "s"),
        ("periodo_maximo_s", per["maximo_s"], "s"),
        ("n_leituras_massa", mas["n_leituras"], "adimensional"),
        ("massa_a_g", mas["a_g"], "g"),
        ("massa_b_g_s", mas["b_g_s"], "g/s"),
        ("massa_tipo_taxa", mas["tipo_taxa"], "texto"),
        ("massa_taxa_g_s", mas["taxa_g_s"], "g/s"),
        ("massa_taxa_g_min", mas["taxa_g_min"], "g/min"),
        ("massa_r2", mas["r2"], "adimensional"),
        ("massa_erro_padrao_b_g_s", mas["erro_padrao_b_g_s"], "g/s"),
        ("massa_erro_padrao_residuos_g", mas["erro_padrao_residuos_g"], "g"),
        ("massa_residuo_max_abs_g", mas["residuo_max_abs_g"], "g"),
        ("massa_status", mas["status"], "texto"),
        ("massa_diagnosticos", mas["diagnosticos"], "texto"),
        ("n_avisos_validacao", len(info["avisos"]), "adimensional"),
        ("graficos_gerados", ";".join(info["graficos"]), "texto"),
        ("graficos_omitidos", ";".join(f"{n}({m})" for n, m in info["graficos_omitidos"]), "texto"),
    ]
    return pd.DataFrame(linhas, columns=["grandeza", "valor", "unidade"])


def processar_filmagem(filmagem: dict, duracao_janela_s: float, pasta_saida: Path) -> dict:
    """Processa uma filmagem válida e grava seus resultados em ``pasta_saida``."""
    pasta_saida = Path(pasta_saida)
    origem = Path(filmagem["pasta"])
    _verificar_saida_fora_dos_dados(pasta_saida, origem)

    id_filmagem = filmagem["id"]
    tracker = filmagem["tracker"]
    massa = filmagem["massa"]
    mergulhos = filmagem["mergulhadas"]
    condicoes = filmagem["condicoes"]

    t_fim = float(max(massa["tempo_seg"].max(), mergulhos["tempo_seg"].max()))
    limites = definir_limites_janelas(t_fim, duracao_janela_s)

    ciclos = construir_ciclos(mergulhos, massa)
    tabela_ciclos = _tabela_ciclos(ciclos, limites)

    ajuste = ajustar_linear(massa["tempo_seg"].to_numpy(dtype=float), massa["massa_g"].to_numpy(dtype=float))
    taxa = taxa_de_perda(ajuste["b_g_s"])
    tabela_ajuste = _tabela_ajuste_global(ajuste, taxa)
    tabela_residuos = _tabela_residuos(massa, ajuste)

    tabela_massa_janelas = ajustar_janelas(massa, limites)
    tabela_periodo_janelas = periodos_por_janela(ciclos, limites)
    estatisticas = estatisticas_periodos(ciclos["periodo_s"].to_numpy(dtype=float))
    n_sem_suporte = int((~ciclos["suporte_massa"].astype(bool)).sum()) if len(ciclos) else 0

    graficos: list[str] = []
    omitidos: list[tuple[str, str]] = []

    def gerar(nome: str, funcao) -> None:
        try:
            funcao(pasta_saida / nome)
        except DadosInsuficientes as exc:
            omitidos.append((nome, exc.motivo))
        else:
            graficos.append(nome)

    gerar(
        "angulo_mergulhos.png",
        lambda caminho: plotar_angulo_mergulhos(tracker, mergulhos, id_filmagem, caminho),
    )
    gerar(
        "massa_ajuste.png",
        lambda caminho: plotar_massa_ajuste(massa, ajuste, id_filmagem, caminho, limites),
    )
    gerar(
        "periodo_tempo.png",
        lambda caminho: plotar_periodo_tempo(ciclos, id_filmagem, caminho, limites),
    )
    gerar(
        "periodo_massa_exploratorio.png",
        lambda caminho: plotar_periodo_massa(ciclos, id_filmagem, caminho),
    )

    info = {
        "id": id_filmagem,
        "condicoes": {
            "liquido": condicoes["liquido"],
            "dia": condicoes["dia"],
            "temperatura_c": condicoes["temperatura_c"],
            "umidade_pct": condicoes["umidade_pct"],
        },
        "t_fim_s": t_fim,
        "duracao_janela_s": float(duracao_janela_s),
        "n_janelas": len(limites),
        "n_mergulhos": len(mergulhos),
        "periodos": estatisticas,
        "n_ciclos_sem_suporte": n_sem_suporte,
        "massa": {
            "n_leituras": ajuste["n"],
            "status": ajuste["status"],
            "a_g": ajuste["a_g"],
            "b_g_s": taxa["b_g_s"],
            "tipo_taxa": taxa["tipo_taxa"],
            "taxa_g_s": taxa["taxa_g_s"],
            "taxa_g_min": taxa["taxa_g_min"],
            "r2": ajuste["r2"],
            "erro_padrao_b_g_s": ajuste["erro_padrao_b_g_s"],
            "erro_padrao_residuos_g": ajuste["erro_padrao_residuos_g"],
            "residuo_max_abs_g": ajuste["residuo_max_abs_g"],
            "diagnosticos": ";".join(ajuste["diagnosticos"]),
        },
        "avisos": [str(p) for p in filmagem.get("avisos", [])],
        "graficos": graficos,
        "graficos_omitidos": omitidos,
    }

    tabelas = {
        "periodos.csv": tabela_ciclos,
        "massa_ajuste.csv": tabela_ajuste,
        "massa_residuos.csv": tabela_residuos,
        "massa_por_janela.csv": tabela_massa_janelas[list(COLUNAS_AJUSTE_JANELA)],
        "periodo_por_janela.csv": tabela_periodo_janelas,
        "resumo.csv": _tabela_resumo(info),
    }
    arquivos = gravar_tabelas(pasta_saida, tabelas, origem=origem)
    arquivos.append(
        gravar_resumo_texto(pasta_saida, montar_resumo_texto(info), origem=origem)
    )

    return {
        "id": id_filmagem,
        "status": "processada",
        "pasta_saida": pasta_saida,
        "arquivos": arquivos,
        "graficos": graficos,
        "graficos_omitidos": omitidos,
        "tabelas": tabelas,
    }
