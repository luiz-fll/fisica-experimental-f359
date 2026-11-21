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

from final.constantes import t_critico_95

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


COLUNAS_CICLOS: tuple[str, ...] = (
    "evento_inicial",
    "evento_final",
    "t_inicial_s",
    "t_final_s",
    "ponto_medio_s",
    "periodo_s",
    "massa_ponto_medio_g",
    "suporte_massa",
)
COLUNAS_ESTATISTICAS_JANELA: tuple[str, ...] = (
    "janela",
    "inicio_s",
    "fim_s",
    "n_ciclos",
    "media_s",
    "desvio_padrao_s",
    "erro_padrao_media_s",
    "ic95_media_inf_s",
    "ic95_media_sup_s",
    "minimo_s",
    "maximo_s",
    "status",
)


def _validar_tempos_crescentes(tempos: np.ndarray, nome: str) -> None:
    """Levanta ``ValueError`` se os tempos não forem finitos e estritamente crescentes."""
    if not np.all(np.isfinite(tempos)):
        raise ValueError(f"{nome}: tempos não finitos")
    if np.any(np.diff(tempos) <= 0):
        raise ValueError(f"{nome}: tempos devem ser estritamente crescentes")


def interpolar_massa(
    tempos_massa: np.ndarray, massas: np.ndarray, tempos_consulta: np.ndarray
) -> np.ndarray:
    """Interpola linearmente a massa nos instantes consultados, sem extrapolação.

    Instantes fora de ``[min, max]`` de ``tempos_massa``, ou não finitos, retornam NaN.
    A máscara de domínio é obrigatória: ``np.interp`` repete o valor da borda fora do
    intervalo e, sem ela, produziria massas inexistentes.
    """
    tm = np.asarray(tempos_massa, dtype=float)
    mm = np.asarray(massas, dtype=float)
    tc = np.asarray(tempos_consulta, dtype=float)
    if tm.ndim != 1 or tm.shape != mm.shape:
        raise ValueError("tempos_massa e massas devem ser vetores de mesmo tamanho")
    if tm.size == 0:
        raise ValueError("massa sem leituras: não há domínio para interpolar")
    _validar_tempos_crescentes(tm, "massa")
    if not np.all(np.isfinite(mm)):
        raise ValueError("massa: valores não finitos")

    dentro = np.isfinite(tc) & (tc >= tm[0]) & (tc <= tm[-1])
    resultado = np.full(tc.shape, np.nan)
    resultado[dentro] = np.interp(tc[dentro], tm, mm)
    return resultado


def construir_ciclos(mergulhadas: pd.DataFrame, massa: pd.DataFrame) -> pd.DataFrame:
    """Constrói a tabela de ciclos entre mergulhos consecutivos.

    Para ``n`` mergulhos em ordem, há ``n-1`` ciclos ``T_i = t_{i+1} - t_i``. Os
    identificadores ``evento_inicial`` e ``evento_final`` são posições 1-based na ordem
    do arquivo; não são lidos do CSV. A massa é interpolada no ponto médio do ciclo,
    somente dentro do domínio de ``massa``; fora dele fica NaN e ``suporte_massa`` é
    falso.

    Retorna DataFrame com as colunas de ``COLUNAS_CICLOS``. Com menos de
    ``MIN_MERGULHOS_PARA_PERIODO`` mergulhos, retorna tabela vazia com as mesmas colunas.

    Levanta ``ValueError`` se os tempos dos mergulhos não forem estritamente crescentes.
    """
    tempos = mergulhadas["tempo_seg"].to_numpy(dtype=float)
    if tempos.size < MIN_MERGULHOS_PARA_PERIODO:
        return pd.DataFrame({c: pd.Series(dtype=float) for c in COLUNAS_CICLOS})
    _validar_tempos_crescentes(tempos, "mergulhadas")

    t_ini = tempos[:-1]
    t_fim = tempos[1:]
    ponto_medio = (t_ini + t_fim) / 2.0
    massa_pm = interpolar_massa(
        massa["tempo_seg"].to_numpy(dtype=float),
        massa["massa_g"].to_numpy(dtype=float),
        ponto_medio,
    )
    return pd.DataFrame(
        {
            "evento_inicial": np.arange(1, tempos.size),
            "evento_final": np.arange(2, tempos.size + 1),
            "t_inicial_s": t_ini,
            "t_final_s": t_fim,
            "ponto_medio_s": ponto_medio,
            "periodo_s": t_fim - t_ini,
            "massa_ponto_medio_g": massa_pm,
            "suporte_massa": np.isfinite(massa_pm),
        }
    )


def estatisticas_periodos(periodos_s: np.ndarray) -> dict:
    """Estatísticas globais de períodos.

    Retorna ``n`` (valores finitos), ``media_s``, ``desvio_padrao_s`` (amostral,
    ``ddof=1``), ``minimo_s`` e ``maximo_s``. Sem dados, ``n=0`` e os demais valores são
    NaN. Com menos de ``MIN_PERIODOS_PARA_DESVIO`` períodos, o desvio é NaN, nunca zero.
    """
    valores = np.asarray(periodos_s, dtype=float)
    valores = valores[np.isfinite(valores)]
    n = int(valores.size)
    if n == 0:
        return {
            "n": 0,
            "media_s": np.nan,
            "desvio_padrao_s": np.nan,
            "erro_padrao_media_s": np.nan,
            "ic95_media_inf_s": np.nan,
            "ic95_media_sup_s": np.nan,
            "minimo_s": np.nan,
            "maximo_s": np.nan,
        }
    desvio = float(valores.std(ddof=1)) if n >= MIN_PERIODOS_PARA_DESVIO else np.nan
    if n >= MIN_PERIODOS_PARA_DESVIO:
        erro_media = desvio / float(np.sqrt(n))
        meia = t_critico_95(n - 1) * erro_media
        media = float(valores.mean())
        ic_inf, ic_sup = media - meia, media + meia
    else:
        erro_media = ic_inf = ic_sup = np.nan
    return {
        "n": n,
        "media_s": float(valores.mean()),
        "desvio_padrao_s": desvio,
        "erro_padrao_media_s": erro_media,
        "ic95_media_inf_s": ic_inf,
        "ic95_media_sup_s": ic_sup,
        "minimo_s": float(valores.min()),
        "maximo_s": float(valores.max()),
    }


def _status_periodos(n: int) -> str:
    if n == 0:
        return "sem_ciclos"
    if n < MIN_PERIODOS_PARA_DESVIO:
        return "sem_desvio"
    return "ok"


def periodos_por_janela(ciclos: pd.DataFrame, limites: pd.DataFrame) -> pd.DataFrame:
    """Agrega períodos por janela, atribuindo cada ciclo pelo ponto médio.

    Todas as janelas de ``limites`` aparecem na saída, mesmo sem ciclos. ``status`` é
    ``sem_ciclos`` (n=0), ``sem_desvio`` (1 ciclo, desvio ausente) ou ``ok``.
    """
    if len(ciclos) > 0:
        atribuidas = atribuir_janela(ciclos["ponto_medio_s"], limites)
        numeros = atribuidas.to_numpy(dtype=object)
    else:
        numeros = np.array([], dtype=object)
    periodos = (
        ciclos["periodo_s"].to_numpy(dtype=float) if len(ciclos) > 0 else np.array([], dtype=float)
    )

    linhas = []
    for _, limite in limites.iterrows():
        mascara = np.array(
            [pd.notna(valor) and int(valor) == int(limite["janela"]) for valor in numeros],
            dtype=bool,
        )
        estat = estatisticas_periodos(periodos[mascara])
        linhas.append(
            {
                "janela": int(limite["janela"]),
                "inicio_s": float(limite["inicio_s"]),
                "fim_s": float(limite["fim_s"]),
                "n_ciclos": estat["n"],
                "media_s": estat["media_s"],
                "desvio_padrao_s": estat["desvio_padrao_s"],
                "erro_padrao_media_s": estat["erro_padrao_media_s"],
                "ic95_media_inf_s": estat["ic95_media_inf_s"],
                "ic95_media_sup_s": estat["ic95_media_sup_s"],
                "minimo_s": estat["minimo_s"],
                "maximo_s": estat["maximo_s"],
                "status": _status_periodos(estat["n"]),
            }
        )
    return pd.DataFrame(linhas, columns=list(COLUNAS_ESTATISTICAS_JANELA))
