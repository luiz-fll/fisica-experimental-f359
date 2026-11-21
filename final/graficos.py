"""Visualizações a partir de resultados já calculados.

Não recalcula nada. Cada figura inclui unidades e identificação. Usa a API orientada a
objetos do matplotlib (sem pyplot e sem janela de interface).

Formatação numérica fixa em todos os rótulos: taxas em g/min com 4 casas decimais,
L·r em W com 3 casas, períodos em s com 2 casas. Não se usa formato geral (`g`), que
suprime zeros à direita e pode fazer valores parecerem de outra ordem de grandeza.

Quando não há dados suficientes, a função levanta ``DadosInsuficientes`` com o motivo,
que o pipeline registra no resumo. Nenhuma figura vazia é gravada.

Por filmagem:
- ``plotar_angulo_mergulhos(tracker, mergulhadas, id_filmagem, caminho)``
- ``plotar_massa_ajuste(massa, ajuste_global, id_filmagem, caminho, limites=None)``
- ``plotar_periodo_tempo(ciclos, id_filmagem, caminho, limites=None)``

Comparação entre filmagens (por dia e entre dias):
- ``plotar_comparacao_massa(series, caminho, titulo)``
- ``plotar_comparacao_periodos(series, caminho, titulo)``
- ``plotar_tau_vs_lr(pontos, caminho, titulo)``
- ``plotar_taxas_janelas(pontos, caminho, titulo)``
- ``plotar_entre_dias(pontos, caminho, titulo)``
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter

from final.massa import MIN_LEITURAS_AJUSTE
from final.periodos import MIN_PERIODOS_PARA_DESVIO

DPI: int = 120
MIN_PONTOS_GRAFICO: int = 2


class DadosInsuficientes(Exception):
    """Dados insuficientes para gerar uma figura. ``motivo`` vai para o resumo."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


def _nova_figura(largura: float = 7.0, altura: float = 4.5, colunas: int = 1) -> Figure:
    figura = Figure(figsize=(largura, altura), constrained_layout=True)
    FigureCanvasAgg(figura)
    return figura


def _salvar(figura: Figure, caminho: Path) -> Path:
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(caminho, dpi=DPI)
    return caminho


def _desenhar_limites(eixo, limites: pd.DataFrame | None) -> None:
    if limites is None or len(limites) <= 1:
        return
    for inicio in limites["inicio_s"].to_numpy(dtype=float)[1:]:
        eixo.axvline(inicio, linestyle="--", color="0.6", linewidth=0.8)


def plotar_angulo_mergulhos(tracker: pd.DataFrame, mergulhadas: pd.DataFrame,
                            id_filmagem: str, caminho: Path) -> Path:
    """Ângulo do tracker em função do tempo, com os mergulhos marcados."""
    if len(tracker) < MIN_PONTOS_GRAFICO:
        raise DadosInsuficientes("tracker com menos de 2 registros")
    figura = _nova_figura()
    eixo = figura.add_subplot(1, 1, 1)
    eixo.plot(tracker["tempo_seg"], tracker["angulo_deg"], color="0.35", linewidth=0.6,
              label="ângulo (tracker)")
    if len(mergulhadas) > 0:
        eixo.scatter(mergulhadas["tempo_seg"], mergulhadas["angulo_deg"], color="C3", s=18,
                     zorder=3, label=f"mergulhos anotados (n={len(mergulhadas)})")
    eixo.set_title(f"{id_filmagem}: ângulo × tempo")
    eixo.set_xlabel("tempo (s)")
    eixo.set_ylabel("ângulo (°)")
    eixo.legend(loc="best", fontsize="small")
    return _salvar(figura, caminho)


def plotar_massa_ajuste(massa: pd.DataFrame, ajuste_global: dict, id_filmagem: str,
                        caminho: Path, limites: pd.DataFrame | None = None) -> Path:
    """Massa em função do tempo, com a reta do ajuste global e o IC95% da taxa."""
    if len(massa) < MIN_LEITURAS_AJUSTE:
        raise DadosInsuficientes(f"massa com {len(massa)} leitura(s); mínimo {MIN_LEITURAS_AJUSTE}")
    if ajuste_global.get("status") != "ok":
        raise DadosInsuficientes(f"ajuste global sem estimativa (status {ajuste_global.get('status')})")
    tempos = massa["tempo_seg"].to_numpy(dtype=float)
    a = ajuste_global["a_g"]
    b = ajuste_global["b_g_s"]
    grade = np.linspace(tempos.min(), tempos.max(), 200)
    taxa_min = -60.0 * b
    rotulo = f"ajuste global: taxa = {taxa_min:.4f} g/min"
    if np.isfinite(ajuste_global.get("ic95_b_g_s_inf", np.nan)):
        inf = -60.0 * ajuste_global["ic95_b_g_s_sup"]
        sup = -60.0 * ajuste_global["ic95_b_g_s_inf"]
        rotulo += f" (IC95% [{inf:.4f}, {sup:.4f}])"
    figura = _nova_figura()
    eixo = figura.add_subplot(1, 1, 1)
    eixo.scatter(tempos, massa["massa_g"], s=14, color="C0", label="leituras de massa")
    eixo.plot(grade, a + b * grade, color="C1", linewidth=1.5, label=rotulo)
    _desenhar_limites(eixo, limites)
    eixo.set_title(f"{id_filmagem}: massa × tempo")
    eixo.set_xlabel("tempo (s)")
    eixo.set_ylabel("massa (g)")
    eixo.legend(loc="best", fontsize="small")
    return _salvar(figura, caminho)


def plotar_periodo_tempo(ciclos: pd.DataFrame, id_filmagem: str, caminho: Path,
                         limites: pd.DataFrame | None = None) -> Path:
    """Período de cada ciclo em função do ponto médio temporal."""
    if len(ciclos) < MIN_PERIODOS_PARA_DESVIO:
        raise DadosInsuficientes(f"{len(ciclos)} ciclo(s); mínimo {MIN_PERIODOS_PARA_DESVIO}")
    figura = _nova_figura()
    eixo = figura.add_subplot(1, 1, 1)
    eixo.plot(ciclos["ponto_medio_s"], ciclos["periodo_s"], "o-", markersize=4, linewidth=0.8, color="C2")
    _desenhar_limites(eixo, limites)
    eixo.set_title(f"{id_filmagem}: período × tempo")
    eixo.set_xlabel("tempo do ponto médio do ciclo (s)")
    eixo.set_ylabel("período (s)")
    return _salvar(figura, caminho)


# ---------------------------------------------------------------------------
# Comparação entre filmagens
# ---------------------------------------------------------------------------


def plotar_comparacao_massa(series: list[dict], caminho: Path, titulo: str) -> Path:
    """Massa × tempo de cada filmagem, com a reta do ajuste global. series: label, t, m, a, b, taxa_min."""
    series = [s for s in series if len(s["t"]) >= MIN_LEITURAS_AJUSTE]
    if not series:
        raise DadosInsuficientes("nenhuma filmagem com leituras suficientes para comparar massas")
    figura = _nova_figura(8.0, 5.0)
    eixo = figura.add_subplot(1, 1, 1)
    for i, s in enumerate(series):
        cor = f"C{i}"
        eixo.scatter(s["t"], s["m"], s=12, color=cor, alpha=0.7)
        grade = np.linspace(min(s["t"]), max(s["t"]), 100)
        eixo.plot(grade, s["a"] + s["b"] * grade, color=cor, linewidth=1.4,
                  label=f"{s['label']}: taxa = {s['taxa_min']:.4f} g/min")
    eixo.set_title(titulo)
    eixo.set_xlabel("tempo (s)")
    eixo.set_ylabel("massa (g)")
    eixo.legend(loc="best", fontsize="small")
    return _salvar(figura, caminho)


def plotar_comparacao_periodos(series: list[dict], caminho: Path, titulo: str) -> Path:
    """Período × tempo do ponto médio, uma curva por filmagem. series: label, ciclos (DataFrame)."""
    series = [s for s in series if len(s["ciclos"]) >= MIN_PERIODOS_PARA_DESVIO]
    if not series:
        raise DadosInsuficientes("nenhuma filmagem com ciclos suficientes para comparar períodos")
    figura = _nova_figura(8.0, 5.0)
    eixo = figura.add_subplot(1, 1, 1)
    for i, s in enumerate(series):
        c = s["ciclos"]
        eixo.plot(c["ponto_medio_s"], c["periodo_s"], "o-", markersize=3, linewidth=0.8,
                  color=f"C{i}", label=s["label"])
    eixo.set_title(titulo)
    eixo.set_xlabel("tempo do ponto médio do ciclo (s)")
    eixo.set_ylabel("período (s)")
    eixo.legend(loc="best", fontsize="small")
    return _salvar(figura, caminho)


def plotar_tau_vs_lr(pontos: list[dict], caminho: Path, titulo: str) -> Path:
    """Período médio τ (com IC95%) em função de L·r (com IC95%), em escala log–log.

    Linha tracejada: τ ∝ 1/(L·r), passando pelo centro geométrico dos pontos, só como
    referência visual da inclinação −1 prevista pelo modelo.
    pontos: label, tau, tau_inf, tau_sup, lr, lr_inf, lr_sup.
    """
    validos = [p for p in pontos if np.isfinite(p["tau"]) and np.isfinite(p["lr"]) and p["lr"] > 0]
    if len(validos) < 2:
        raise DadosInsuficientes("menos de 2 pontos com período e L·r definidos")
    figura = _nova_figura(6.5, 5.0)
    eixo = figura.add_subplot(1, 1, 1)
    for i, p in enumerate(validos):
        eixo.errorbar(p["lr"], p["tau"],
                      xerr=[[p["lr"] - p["lr_inf"]], [p["lr_sup"] - p["lr"]]],
                      yerr=[[p["tau"] - p["tau_inf"]], [p["tau_sup"] - p["tau"]]],
                      fmt="o", color=f"C{i}", capsize=3, label=p["label"])
    xs = np.array([p["lr"] for p in validos])
    ys = np.array([p["tau"] for p in validos])
    k = float(np.exp(np.mean(np.log(ys * xs))))
    grade = np.geomspace(xs.min() * 0.9, xs.max() * 1.1, 50)
    eixo.plot(grade, k / grade, "--", color="0.5", linewidth=1.0, label="τ ∝ 1/(L·r) (referência)")
    eixo.set_xscale("log")
    eixo.set_yscale("log")
    for eixo_escala in (eixo.xaxis, eixo.yaxis):
        formatador = ScalarFormatter()
        formatador.set_scientific(False)
        eixo_escala.set_major_formatter(formatador)
        eixo_escala.set_minor_formatter(ScalarFormatter())
    eixo.set_title(titulo)
    eixo.set_xlabel("L·r (W)")
    eixo.set_ylabel("período médio τ (s)")
    eixo.legend(loc="best", fontsize="small")
    return _salvar(figura, caminho)


def plotar_taxas_janelas(pontos: list[dict], caminho: Path, titulo: str) -> Path:
    """Taxa de perda (g/min, com IC95%) por janela de cada filmagem.

    pontos: label, janela (int), taxa_min, taxa_inf, taxa_sup (NaN quando não há perda).
    """
    validos = [p for p in pontos if np.isfinite(p["taxa_min"])]
    if not validos:
        raise DadosInsuficientes("nenhuma janela com taxa de perda definida")
    figura = _nova_figura(8.0, 4.8)
    eixo = figura.add_subplot(1, 1, 1)
    rotulos = sorted({p["label"] for p in validos})
    janelas = sorted({int(p["janela"]) for p in validos})
    largura = 0.8 / max(1, len(rotulos))
    for i, rotulo in enumerate(rotulos):
        xs, ys, erros = [], [], [[], []]
        for p in validos:
            if p["label"] != rotulo:
                continue
            xs.append(int(p["janela"]) + (i - (len(rotulos) - 1) / 2) * largura)
            ys.append(p["taxa_min"])
            erros[0].append(p["taxa_min"] - p["taxa_inf"])
            erros[1].append(p["taxa_sup"] - p["taxa_min"])
        eixo.errorbar(xs, ys, yerr=erros, fmt="o", capsize=3, color=f"C{i}", label=rotulo)
    eixo.set_xticks(janelas)
    eixo.set_xlabel("janela (índice)")
    eixo.set_ylabel("taxa de perda de massa (g/min)")
    eixo.set_title(titulo)
    eixo.legend(loc="best", fontsize="small")
    return _salvar(figura, caminho)


def plotar_entre_dias(pontos: list[dict], caminho: Path, titulo: str) -> Path:
    """Período (painel esquerdo) e taxa de perda (painel direito) de cada líquido nos três dias.

    pontos: liquido, dia (rótulo do eixo x), tau, tau_inf, tau_sup, taxa_min, taxa_inf, taxa_sup.
    """
    validos = [p for p in pontos if np.isfinite(p["tau"]) or np.isfinite(p["taxa_min"])]
    if not validos:
        raise DadosInsuficientes("nenhum ponto com período ou taxa definidos")
    dias = sorted({p["dia"] for p in validos})
    liquidos = sorted({p["liquido"] for p in validos})
    figura = Figure(figsize=(10.0, 4.5), constrained_layout=True)
    FigureCanvasAgg(figura)
    eixo_tau = figura.add_subplot(1, 2, 1)
    eixo_taxa = figura.add_subplot(1, 2, 2)
    for i, liquido in enumerate(liquidos):
        mesmos = [p for p in validos if p["liquido"] == liquido]
        xs = [dias.index(p["dia"]) + (i - (len(liquidos) - 1) / 2) * 0.12 for p in mesmos]
        tau = [p["tau"] for p in mesmos]
        eixo_tau.errorbar(xs, tau,
                          yerr=[[p["tau"] - p["tau_inf"] for p in mesmos],
                                [p["tau_sup"] - p["tau"] for p in mesmos]],
                          fmt="o", capsize=3, color=f"C{i}", label=liquido)
        taxa = [p["taxa_min"] for p in mesmos]
        eixo_taxa.errorbar(xs, taxa,
                           yerr=[[p["taxa_min"] - p["taxa_inf"] for p in mesmos],
                                 [p["taxa_sup"] - p["taxa_min"] for p in mesmos]],
                           fmt="o", capsize=3, color=f"C{i}", label=liquido)
    for eixo, ylabel in ((eixo_tau, "período médio τ (s)"), (eixo_taxa, "taxa de perda (g/min)")):
        eixo.set_xticks(range(len(dias)))
        eixo.set_xticklabels(dias)
        eixo.set_xlabel("dia do ensaio")
        eixo.set_ylabel(ylabel)
        eixo.legend(loc="best", fontsize="small")
    eixo_tau.set_title("Período por dia (IC95%)")
    eixo_taxa.set_title("Taxa de perda por dia (IC95%)")
    figura.suptitle(titulo)
    return _salvar(figura, caminho)
