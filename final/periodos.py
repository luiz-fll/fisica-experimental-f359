"""Períodos de mergulho, associação com a massa e janelas temporais.

Convenção de janelas (implementada neste módulo):

- A origem temporal do ensaio é ``ORIGEM_TEMPORAL_S`` (0 s, referência comum dos
  ``tempo_seg`` dos CSVs). A origem não é reancorada em cada arquivo.
- As janelas são ``[inicio, fim)``, com duração ``duracao`` configurável (padrão 200 s).
- O número de janelas é ``N = max(1, floor(t_fim / duracao))``, em que ``t_fim`` é o
  maior instante observado na filmagem (massa ou mergulhos).
- A última janela absorve o resto do ensaio: ``[(N-1)*duracao, t_fim]``, fechada à
  direita para incluir o último instante. Ela tem duração entre ``duracao`` e
  ``2*duracao`` (exclusive). Não há janela com menos de ``duracao`` segundos, exceto
  quando o ensaio inteiro é mais curto que ``duracao``.
- Cada ciclo é atribuído à janela que contém seu ponto médio temporal.
- Janelas numeradas de 1 a N. Instantes negativos ou não finitos não pertencem a
  nenhuma janela.

Mínimos (contrato; estatísticas a implementar):

- ``MIN_MERGULHOS_PARA_PERIODO``: pelo menos 2 mergulhos para existir um período.
- ``MIN_PERIODOS_PARA_DESVIO``: pelo menos 2 períodos para o desvio-padrão amostral
  (``ddof=1``). Com menos, o desvio é registrado como ausente, nunca como zero.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

ORIGEM_TEMPORAL_S: float = 0.0
DURACAO_JANELA_PADRAO_S: float = 200.0
MIN_MERGULHOS_PARA_PERIODO: int = 2
MIN_PERIODOS_PARA_DESVIO: int = 2

_TOLERANCIA_NUMERICA = 1e-9


def definir_limites_janelas(
    t_fim: float, duracao: float = DURACAO_JANELA_PADRAO_S
) -> pd.DataFrame:
    """Gera os limites das janelas temporais de uma filmagem.

    Parâmetros
    ----------
    t_fim:
        Maior instante observado na filmagem, em segundos. Finito e >= 0.
    duracao:
        Duração de cada janela em segundos. Finita e > 0.

    Retorna
    -------
    DataFrame com colunas ``janela`` (int, 1..N), ``inicio_s``, ``fim_s`` (float) e
    ``fechada_direita`` (bool, verdadeiro somente na última janela).

    Levanta
    -------
    ValueError
        Se ``t_fim`` ou ``duracao`` forem inválidos.
    """
    if not math.isfinite(t_fim) or t_fim < ORIGEM_TEMPORAL_S:
        raise ValueError(f"t_fim deve ser finito e >= {ORIGEM_TEMPORAL_S}; recebido {t_fim!r}")
    if not math.isfinite(duracao) or duracao <= 0:
        raise ValueError(f"duracao deve ser finita e > 0; recebida {duracao!r}")

    n_janelas = max(1, math.floor((t_fim - ORIGEM_TEMPORAL_S) / duracao + _TOLERANCIA_NUMERICA))
    # A tolerância não pode criar uma janela que começa depois de t_fim.
    if n_janelas > 1 and ORIGEM_TEMPORAL_S + (n_janelas - 1) * duracao > t_fim:
        n_janelas -= 1

    indices = np.arange(n_janelas)
    inicios = ORIGEM_TEMPORAL_S + indices * duracao
    fins = inicios + duracao
    fins[-1] = ORIGEM_TEMPORAL_S + t_fim  # a última janela absorve o resto do ensaio
    return pd.DataFrame(
        {
            "janela": indices + 1,
            "inicio_s": inicios.astype(float),
            "fim_s": fins.astype(float),
            "fechada_direita": indices == n_janelas - 1,
        }
    )


def atribuir_janela(tempos: pd.Series | np.ndarray, limites: pd.DataFrame) -> pd.Series:
    """Associa instantes às janelas definidas por ``definir_limites_janelas``.

    Retorna ``pd.Series`` de inteiros anuláveis (``Int64``) com o número da janela de
    cada instante. Instantes fora de ``[origem, último fim]``, negativos ou não
    finitos recebem ``<NA>``.
    """
    t = pd.to_numeric(pd.Series(np.asarray(tempos, dtype=float)), errors="coerce").to_numpy(
        dtype=float
    )
    inicios = limites["inicio_s"].to_numpy(dtype=float)
    fins = limites["fim_s"].to_numpy(dtype=float)
    numeros = limites["janela"].to_numpy(dtype=np.int64)

    dentro = np.isfinite(t) & (t >= inicios[0]) & (t <= fins[-1])
    posicao = np.searchsorted(inicios, t, side="right") - 1
    posicao = np.clip(posicao, 0, len(inicios) - 1)

    resultado = np.full(len(t), -1, dtype=np.int64)
    resultado[dentro] = numeros[posicao[dentro]]
    saida = pd.array(resultado, dtype="Int64")
    saida[~dentro] = pd.NA
    return pd.Series(saida, name="janela")


def construir_ciclos(mergulhadas: pd.DataFrame, massa: pd.DataFrame) -> pd.DataFrame:
    """Constrói a tabela de ciclos entre mergulhos consecutivos (contrato).

    A implementar: ``T_i = t_{i+1} - t_i`` para eventos consecutivos, com colunas
    mínimas ``evento_inicial``, ``evento_final``, ``t_inicial_s``, ``t_final_s``,
    ``ponto_medio_s``, ``periodo_s`` e ``massa_ponto_medio_g`` (ausente sem suporte).
    """
    raise NotImplementedError("construir_ciclos: a implementar na etapa de cálculos.")


def interpolar_massa(
    tempos_massa: np.ndarray, massas: np.ndarray, tempos_consulta: np.ndarray
) -> np.ndarray:
    """Interpola linearmente a massa nos instantes consultados (contrato).

    Instantes fora de ``[min, max]`` de ``tempos_massa`` retornam NaN (sem extrapolação).
    """
    raise NotImplementedError("interpolar_massa: a implementar na etapa de cálculos.")


def estatisticas_periodos(periodos_s: np.ndarray) -> dict:
    """Estatísticas globais de períodos (contrato).

    Retorna ``n``, ``media_s``, ``desvio_padrao_s`` (amostral, ``ddof=1``), ``minimo_s``
    e ``maximo_s``. Sem dados, ``n=0`` e valores ausentes. Com menos de
    ``MIN_PERIODOS_PARA_DESVIO`` períodos, ``desvio_padrao_s`` é ausente.
    """
    raise NotImplementedError("estatisticas_periodos: a implementar na etapa de cálculos.")


def periodos_por_janela(ciclos: pd.DataFrame, limites: pd.DataFrame) -> pd.DataFrame:
    """Agrega períodos por janela, pelo ponto médio de cada ciclo (contrato).

    Todas as janelas de ``limites`` aparecem na saída, mesmo sem ciclos (com ``n=0``).
    """
    raise NotImplementedError("periodos_por_janela: a implementar na etapa de cálculos.")
