"""Comparação entre filmagens: dia a dia (principal) e entre dias (ambiente).

Justificativa do módulo: a comparação entre filmagens não pertence a nenhuma filmagem
isolada; é uma responsabilidade própria, separada de ``pipeline.py``.

Decisões de análise (2026-11-20, do pesquisador):

- A comparação principal é feita **dia a dia**: em cada dia há um pássaro e um líquido
  por filmagem, e as condições ambientais são as do próprio dia. Isso isola diferenças
  entre líquidos das variações de ambiente entre dias.
- A variação entre dias é reportada à parte, para mostrar o efeito de ambiente.
- O líquido "álcool 70%" é etanol a 70 % em massa (w/w) em água; "álcool 99%" é isopropanol.
- O calor latente vem do NIST (``constantes.py``).

Nada aqui é uma verificação de hipótese. As ordenações previstas (H2 e a relação
τ ∝ 1/(L·r)) são registradas como comparações descritivas; a inclinação log–log com três
pontos por dia é apenas descritiva, sem inferência.

Saídas, em ``<saida>/comparacao/``:
- ``por_dia/<dia>/comparacao_dia.csv``: uma linha por filmagem do dia.
- ``por_dia/<dia>/hipoteses_dia.csv``: ordenações observadas e previstas, descritivas.
- ``por_dia/<dia>/grafico_*.png``: massa, períodos, τ × L·r, taxas por janela.
- ``entre_dias/variacao_por_liquido.csv`` e ``grafico_entre_dias.png``.
- ``entre_dias/pares_janela.csv``: pares (período, L·r) por janela, todos os dias.
- ``leia_me.txt``: o que foi gerado e o que foi omitido, com motivo.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from final.graficos import (
    DadosInsuficientes,
    plotar_comparacao_massa,
    plotar_comparacao_periodos,
    plotar_entre_dias,
    plotar_taxas_janelas,
    plotar_tau_vs_lr,
)
from final.periodos import estatisticas_periodos

ORDEM_H2_PREVISTA: tuple[str, ...] = ("alcool 99%", "alcool 70%", "agua")  # τ crescente, relatório parcial


def _linha_filmagem(item: dict) -> dict:
    """Grandezas por filmagem, lidas das tabelas já calculadas pelo pipeline."""
    tab = item["tabelas"]
    ciclos = tab["periodos.csv"]
    estat = estatisticas_periodos(ciclos["periodo_s"].to_numpy(dtype=float)) if len(ciclos) else None
    ajuste = tab["massa_ajuste.csv"].iloc[0]
    cond = item["condicoes"]
    return {
        "id": item["id"],
        "liquido": cond["liquido"],
        "dia": cond["dia"],
        "temperatura_c": float(cond["temperatura_c"]),
        "umidade_pct": float(cond["umidade_pct"]),
        "n_ciclos": int(estat["n"]) if estat else 0,
        "tau_media_s": estat["media_s"] if estat else np.nan,
        "tau_ic95_inf_s": estat["ic95_media_inf_s"] if estat else np.nan,
        "tau_ic95_sup_s": estat["ic95_media_sup_s"] if estat else np.nan,
        "tau_desvio_padrao_s": estat["desvio_padrao_s"] if estat else np.nan,
        "taxa_g_min": ajuste["taxa_g_min"],
        "taxa_ic95_inf_g_min": ajuste["ic95_taxa_g_min_inf"],
        "taxa_ic95_sup_g_min": ajuste["ic95_taxa_g_min_sup"],
        "L_kj_kg": ajuste["L_kj_kg"],
        "L_r_W": ajuste["L_r_W"],
        "L_r_ic95_inf_W": ajuste["L_r_ic95_inf_W"],
        "L_r_ic95_sup_W": ajuste["L_r_ic95_sup_W"],
        "L_r_alternativo_W": ajuste["L_r_alternativo_W"],
    }


def _hipoteses(linhas: pd.DataFrame) -> pd.DataFrame:
    """Ordenações e concordâncias do dia, descritivas. Não são testes de hipótese."""
    com_tau = linhas.dropna(subset=["tau_media_s"])
    ordem_obs = com_tau.sort_values("tau_media_s")["liquido"].tolist()
    com_lr = com_tau.dropna(subset=["L_r_W"])
    ordem_lr = com_lr.sort_values("L_r_W", ascending=False)["liquido"].tolist()  # maior L·r → menor τ
    presentes = [l for l in ORDEM_H2_PREVISTA if l in ordem_obs]
    h2_obs = [l for l in ordem_obs if l in presentes]

    sobrepostos = []
    for i, a in enumerate(com_tau.itertuples()):
        for b in list(com_tau.itertuples())[i + 1:]:
            sobrepostos.append(
                f"{a.liquido} x {b.liquido}: "
                + ("IC95% se sobrepõem" if (a.tau_ic95_inf_s <= b.tau_ic95_sup_s and b.tau_ic95_inf_s <= a.tau_ic95_sup_s)
                   else "IC95% não se sobrepõem")
            )

    inclinacao = np.nan
    if len(com_lr) >= 2:
        inclinacao = float(np.polyfit(np.log(com_lr["L_r_W"]), np.log(com_lr["tau_media_s"]), 1)[0])

    return pd.DataFrame([{
        "liquidos_no_dia": int(len(com_tau)),
        "ordem_tau_observada_crescente": " < ".join(ordem_obs),
        "ordem_H2_prevista_crescente": " < ".join(ORDEM_H2_PREVISTA),
        "ordem_observada_coincide_com_H2_prevista": bool(h2_obs == presentes) if len(presentes) == len(ordem_obs) else np.nan,
        "ordem_tau_prevista_por_L_r_crescente": " < ".join(ordem_lr),
        "ordem_observada_coincide_com_L_r_previsto": bool(ordem_obs == ordem_lr) if len(ordem_lr) == len(ordem_obs) else np.nan,
        "inclinacao_log_tau_vs_log_L_r": inclinacao,
        "inclinacao_esperada_pelo_modelo": -1.0,
        "ic95_sobreposicao": "; ".join(sobrepostos),
        "nota": "Descritivo: n = 3 por dia; não é teste de hipótese.",
    }])


def _pares_janela(item: dict) -> pd.DataFrame:
    per = item["tabelas"]["periodo_por_janela.csv"]
    mas = item["tabelas"]["massa_por_janela.csv"]
    junto = per.merge(mas[["janela", "taxa_g_min", "L_r_W", "L_r_ic95_inf_W", "L_r_ic95_sup_W"]],
                      on="janela", how="left")
    junto = junto.rename(columns={
        "media_s": "tau_media_s",
        "desvio_padrao_s": "tau_desvio_padrao_s",
        "ic95_media_inf_s": "tau_ic95_inf_s",
        "ic95_media_sup_s": "tau_ic95_sup_s",
    })
    junto.insert(0, "dia", item["condicoes"]["dia"])
    junto.insert(0, "liquido", item["condicoes"]["liquido"])
    junto.insert(0, "id", item["id"])
    return junto


def gerar_comparacao(processadas: list[dict], pasta_saida: Path) -> list[Path]:
    """Gera as tabelas e figuras de comparação. Retorna os arquivos gravados."""
    pasta_saida = Path(pasta_saida) / "comparacao"
    gravados: list[Path] = []
    omitidos: list[str] = []
    if not processadas:
        raise ValueError("nenhuma filmagem processada para comparar")

    linhas = pd.DataFrame([_linha_filmagem(it) for it in processadas])
    itens = {it["id"]: it for it in processadas}

    for dia, grupo in linhas.groupby("dia", sort=True):
        pasta_dia = pasta_saida / "por_dia" / str(dia)
        pasta_dia.mkdir(parents=True, exist_ok=True)
        grupo = grupo.sort_values("liquido")
        destino = pasta_dia / "comparacao_dia.csv"
        grupo.to_csv(destino, index=False)
        gravados.append(destino)

        hip = _hipoteses(grupo)
        destino = pasta_dia / "hipoteses_dia.csv"
        hip.to_csv(destino, index=False)
        gravados.append(destino)

        membros = [itens[i] for i in grupo["id"]]
        series_massa = []
        series_per = []
        pontos_lr = []
        pontos_janela = []
        for it, (_, r) in zip(membros, grupo.iterrows()):
            ajuste = it["tabelas"]["massa_ajuste.csv"].iloc[0]
            m = it["massa_df"]
            series_massa.append({
                "label": r["liquido"], "t": m["tempo_seg"].to_numpy(float),
                "m": m["massa_g"].to_numpy(float), "a": ajuste["a_g"], "b": ajuste["b_g_s"],
                "taxa_min": ajuste["taxa_g_min"],
            })
            series_per.append({"label": r["liquido"], "ciclos": it["tabelas"]["periodos.csv"]})
            pontos_lr.append({
                "label": r["liquido"], "tau": r["tau_media_s"], "tau_inf": r["tau_ic95_inf_s"],
                "tau_sup": r["tau_ic95_sup_s"], "lr": r["L_r_W"], "lr_inf": r["L_r_ic95_inf_W"],
                "lr_sup": r["L_r_ic95_sup_W"],
            })
            per = it["tabelas"]["periodo_por_janela.csv"]
            mas = it["tabelas"]["massa_por_janela.csv"]
            for (_, pj), (_, mj) in zip(per.iterrows(), mas.iterrows()):
                pontos_janela.append({"label": r["liquido"], "janela": int(pj["janela"]),
                                      "taxa_min": mj["taxa_g_min"], "taxa_inf": mj["ic95_taxa_g_min_inf"],
                                      "taxa_sup": mj["ic95_taxa_g_min_sup"]})

        for nome, funcao in (
            ("grafico_massa.png", lambda c: plotar_comparacao_massa(series_massa, c, f"Massa × tempo — {dia}")),
            ("grafico_periodos.png", lambda c: plotar_comparacao_periodos(series_per, c, f"Períodos — {dia}")),
            ("grafico_tau_vs_lr.png", lambda c: plotar_tau_vs_lr(pontos_lr, c, f"τ × L·r — {dia}")),
            ("grafico_taxas_janelas.png", lambda c: plotar_taxas_janelas(pontos_janela, c, f"Taxa por janela — {dia}")),
        ):
            try:
                gravados.append(funcao(pasta_dia / nome))
            except DadosInsuficientes as exc:
                omitidos.append(f"por_dia/{dia}/{nome}: {exc.motivo}")

    pasta_ent = pasta_saida / "entre_dias"
    pasta_ent.mkdir(parents=True, exist_ok=True)
    variacao = linhas.sort_values(["liquido", "dia"])[[
        "liquido", "dia", "temperatura_c", "umidade_pct", "n_ciclos", "tau_media_s", "tau_ic95_inf_s",
        "tau_ic95_sup_s", "taxa_g_min", "taxa_ic95_inf_g_min", "taxa_ic95_sup_g_min", "L_r_W",
        "L_r_ic95_inf_W", "L_r_ic95_sup_W",
    ]]
    destino = pasta_ent / "variacao_por_liquido.csv"
    variacao.to_csv(destino, index=False)
    gravados.append(destino)

    pontos_dia = [{
        "liquido": r["liquido"], "dia": r["dia"], "tau": r["tau_media_s"], "tau_inf": r["tau_ic95_inf_s"],
        "tau_sup": r["tau_ic95_sup_s"], "taxa_min": r["taxa_g_min"], "taxa_inf": r["taxa_ic95_inf_g_min"],
        "taxa_sup": r["taxa_ic95_sup_g_min"],
    } for _, r in linhas.iterrows()]
    try:
        gravados.append(plotar_entre_dias(pontos_dia, pasta_ent / "grafico_entre_dias.png",
                                          "Variação entre dias por líquido"))
    except DadosInsuficientes as exc:
        omitidos.append(f"entre_dias/grafico_entre_dias.png: {exc.motivo}")

    pares = pd.concat([_pares_janela(it) for it in processadas], ignore_index=True)
    destino = pasta_ent / "pares_janela.csv"
    pares.to_csv(destino, index=False)
    gravados.append(destino)

    leia = pasta_saida / "leia_me.txt"
    texto = [
        "Comparação entre filmagens (gerada automaticamente).",
        "Principal: por_dia/ (líquidos no mesmo dia, mesmas condições). Ambiente: entre_dias/.",
        "Líquidos: 'agua'; 'alcool 70%' = etanol a 70 % em massa (w/w); 'alcool 99%' = isopropanol.",
        "L: NIST (constantes.py). L·r em W; IC95% por propagação de primeira ordem.",
        "Ordenações e inclinações em hipoteses_dia.csv são descritivas (n = 3 por dia).",
        "",
        "Figuras omitidas (motivo):" if omitidos else "Nenhuma figura omitida.",
    ] + [f"  - {o}" for o in omitidos]
    leia.write_text("\n".join(texto) + "\n", encoding="utf-8")
    gravados.append(leia)
    return gravados
