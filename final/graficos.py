"""Visualizações a partir de resultados já calculados.

Não recalcula períodos, ajustes ou estatísticas. Cada figura inclui unidades e o
identificador da filmagem. Usa a API orientada a objetos do matplotlib (sem
``pyplot`` e sem janela de interface), para funcionar em qualquer ambiente.

Quando não há dados suficientes, a função levanta ``DadosInsuficientes`` com o motivo,
que o pipeline registra no resumo. Nenhuma figura vazia é gravada.

Funções:

- ``plotar_angulo_mergulhos(tracker, mergulhadas, id_filmagem, caminho)``
- ``plotar_massa_ajuste(massa, ajuste_global, id_filmagem, caminho, limites=None)``
- ``plotar_periodo_tempo(ciclos, id_filmagem, caminho, limites=None)``
- ``plotar_periodo_massa(ciclos, id_filmagem, caminho)`` (exploratório)

Limites de janela (``limites``), quando passados, são desenhados como linhas
tracejadas nos instantes de início das janelas posteriores à primeira.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from final.periodos import MIN_PERIODOS_PARA_DESVIO
from final.massa import MIN_LEITURAS_AJUSTE

DPI: int = 120
MIN_PONTOS_GRAFICO: int = 2


class DadosInsuficientes(Exception):
    """Dados insuficientes para gerar uma figura. ``motivo`` vai para o resumo."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


def _nova_figura() -> Figure:
    figura = Figure(figsize=(7.0, 4.5), constrained_layout=True)
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


def plotar_angulo_mergulhos(
    tracker: pd.DataFrame,
    mergulhadas: pd.DataFrame,
    id_filmagem: str,
    caminho: Path,
) -> Path:
    """Ângulo do tracker em função do tempo, com os mergulhos marcados."""
    if len(tracker) < MIN_PONTOS_GRAFICO:
        raise DadosInsuficientes("tracker com menos de 2 registros")

    figura = _nova_figura()
    eixo = figura.add_subplot(1, 1, 1)
    eixo.plot(tracker["tempo_seg"], tracker["angulo_deg"], color="0.35", linewidth=0.6, label="ângulo (tracker)")
    if len(mergulhadas) > 0:
        eixo.scatter(
            mergulhadas["tempo_seg"],
            mergulhadas["angulo_deg"],
            color="C3",
            s=18,
            zorder=3,
            label=f"mergulhos anotados (n={len(mergulhadas)})",
        )
    eixo.set_title(f"{id_filmagem}: ângulo × tempo")
    eixo.set_xlabel("tempo (s)")
    eixo.set_ylabel("ângulo (°)")
    eixo.legend(loc="best", fontsize="small")
    return _salvar(figura, caminho)


def plotar_massa_ajuste(
    massa: pd.DataFrame,
    ajuste_global: dict,
    id_filmagem: str,
    caminho: Path,
    limites: pd.DataFrame | None = None,
) -> Path:
    """Massa em função do tempo, com a reta do ajuste global."""
    if len(massa) < MIN_LEITURAS_AJUSTE:
        raise DadosInsuficientes(f"massa com {len(massa)} leitura(s); mínimo {MIN_LEITURAS_AJUSTE}")
    if ajuste_global.get("status") != "ok":
        raise DadosInsuficientes(f"ajuste global sem estimativa (status {ajuste_global.get('status')})")

    tempos = massa["tempo_seg"].to_numpy(dtype=float)
    a = ajuste_global["a_g"]
    b = ajuste_global["b_g_s"]
    grade = np.linspace(tempos.min(), tempos.max(), 200)

    figura = _nova_figura()
    eixo = figura.add_subplot(1, 1, 1)
    eixo.scatter(tempos, massa["massa_g"], s=14, color="C0", label="leituras de massa")
    eixo.plot(grade, a + b * grade, color="C1", linewidth=1.5, label=f"ajuste global: b = {b:.4g} g/s")
    _desenhar_limites(eixo, limites)
    eixo.set_title(f"{id_filmagem}: massa × tempo")
    eixo.set_xlabel("tempo (s)")
    eixo.set_ylabel("massa (g)")
    eixo.legend(loc="best", fontsize="small")
    return _salvar(figura, caminho)


def plotar_periodo_tempo(
    ciclos: pd.DataFrame,
    id_filmagem: str,
    caminho: Path,
    limites: pd.DataFrame | None = None,
) -> Path:
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


def plotar_periodo_massa(
    ciclos: pd.DataFrame,
    id_filmagem: str,
    caminho: Path,
) -> Path:
    """Período em função da massa interpolada no ponto médio (exploratório).

    Usa apenas ciclos com suporte de massa. Não é uma verificação da hipótese.
    """
    com_suporte = ciclos[ciclos["suporte_massa"].astype(bool)]
    if len(com_suporte) < MIN_PERIODOS_PARA_DESVIO:
        raise DadosInsuficientes(
            f"{len(com_suporte)} ciclo(s) com massa interpolada; mínimo {MIN_PERIODOS_PARA_DESVIO}"
        )

    figura = _nova_figura()
    eixo = figura.add_subplot(1, 1, 1)
    eixo.scatter(com_suporte["massa_ponto_medio_g"], com_suporte["periodo_s"], s=16, color="C4")
    eixo.set_title(f"{id_filmagem}: período × massa (exploratório)")
    eixo.set_xlabel("massa interpolada no ponto médio (g)")
    eixo.set_ylabel("período (s)")
    return _salvar(figura, caminho)
