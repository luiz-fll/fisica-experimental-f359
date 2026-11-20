"""CLI, descoberta, leitura e validação das filmagens.

Este módulo lê e valida; não faz cálculos científicos. Cada filmagem é
processada de forma isolada: um erro em uma pasta é registrado e o lote segue.

Fluxo:

1. ``main`` interpreta ``--diretorio``, ``--saida`` e ``--janela``.
2. ``descobrir_filmagens`` lista as subpastas diretas do diretório.
3. ``validar_lote`` chama ``carregar_filmagem`` para cada pasta, isolando falhas.
4. ``carregar_filmagem`` lê cada um dos quatro CSVs uma única vez e valida tudo
   em memória. Nenhum arquivo de dados é modificado, e o ``.trk`` nunca é lido.
5. Cada filmagem válida é processada por ``pipeline.processar_filmagem``, que grava
   em ``--saida/<id>``. Uma falha de processamento é isolada, como a de validação.

Não há correção silenciosa de dados: valores e cabeçalhos são aceitos como estão ou
reportados como erro. Problemas de qualidade que não impedem a análise são avisos.

Códigos de saída da CLI: 0 se todas as filmagens são válidas e foram processadas;
1 se alguma é inválida ou falhou no processamento; 2 para erro de uso ou de
configuração (diretório inexistente, saída dentro dos dados, janela inválida, nenhuma
filmagem encontrada).
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from final.massa import MIN_LEITURAS_AJUSTE
from final.pipeline import processar_filmagem
from final.periodos import (
    DURACAO_JANELA_PADRAO_S,
    MIN_MERGULHOS_PARA_PERIODO,
    ORIGEM_TEMPORAL_S,
)

DIR_BASE = Path(__file__).resolve().parent
DIR_DADOS_PADRAO = DIR_BASE / "dados"
DIR_RESULTADOS_PADRAO = DIR_BASE / "resultados"

# Cabeçalhos exatos, na ordem observada nos dados reais (AGENTS.md, PROJECT.md seção 4).
ARQUIVOS_OBRIGATORIOS: dict[str, tuple[str, ...]] = {
    "tracker.csv": ("tempo_seg", "angulo_deg"),
    "massa.csv": ("tempo_seg", "massa_g"),
    "mergulhadas.csv": ("tempo_seg", "angulo_deg"),
    "condicoes.csv": ("liquido", "dia", "temperatura_c", "umidade_pct"),
}

MIN_LINHAS_TRACKER: int = 2
TOLERANCIA_ANGULO_EVENTO_GRAUS: float = 2.0
MAX_EXEMPLOS_NA_MENSAGEM: int = 5

ERRO = "erro"
AVISO = "aviso"


@dataclass(frozen=True)
class Problema:
    """Achado de validação, identificado pelo arquivo de origem."""

    arquivo: str
    gravidade: str
    mensagem: str

    def __str__(self) -> str:
        return f"{self.arquivo}: {self.mensagem}"


class ErroFilmagem(Exception):
    """Filmagem inválida. Carrega todos os problemas encontrados, com arquivo identificado."""

    def __init__(self, pasta: Path, problemas: list[Problema]) -> None:
        self.pasta = pasta
        self.problemas = list(problemas)
        erros = [p for p in self.problemas if p.gravidade == ERRO]
        resumo = "; ".join(str(p) for p in erros) or "erro não especificado"
        super().__init__(f"[{pasta.name}] {resumo}")

    @property
    def erros(self) -> list[Problema]:
        return [p for p in self.problemas if p.gravidade == ERRO]

    @property
    def avisos(self) -> list[Problema]:
        return [p for p in self.problemas if p.gravidade == AVISO]


# ---------------------------------------------------------------------------
# Descoberta
# ---------------------------------------------------------------------------


def descobrir_filmagens(diretorio: Path) -> list[Path]:
    """Retorna as subpastas diretas de ``diretorio``, ordenadas e sem pastas ocultas.

    Levanta ``NotADirectoryError`` se ``diretorio`` não existir ou não for uma pasta.
    """
    diretorio = Path(diretorio)
    if not diretorio.is_dir():
        raise NotADirectoryError(f"diretório inexistente ou não é uma pasta: {diretorio}")
    return sorted(
        p for p in diretorio.iterdir() if p.is_dir() and not p.name.startswith(".")
    )


# ---------------------------------------------------------------------------
# Leitura e validação de um arquivo
# ---------------------------------------------------------------------------


def _ler_csv(pasta: Path, nome: str, problemas: list[Problema]) -> pd.DataFrame | None:
    """Lê um CSV como texto, sem conversão, e valida cabeçalho e presença de linhas."""
    caminho = pasta / nome
    if not caminho.is_file():
        problemas.append(Problema(nome, ERRO, "arquivo ausente"))
        return None
    esperado = list(ARQUIVOS_OBRIGATORIOS[nome])
    try:
        df = pd.read_csv(caminho, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        problemas.append(Problema(nome, ERRO, "arquivo vazio (sem cabeçalho)"))
        return None
    except pd.errors.ParserError as exc:
        problemas.append(
            Problema(nome, ERRO, f"número de campos inconsistente nas linhas: {exc}")
        )
        return None
    except UnicodeDecodeError:
        problemas.append(Problema(nome, ERRO, "arquivo não está codificado em UTF-8"))
        return None
    except OSError as exc:
        problemas.append(Problema(nome, ERRO, f"arquivo não pode ser lido: {exc}"))
        return None

    if list(df.columns) != esperado:
        problemas.append(
            Problema(
                nome,
                ERRO,
                f"cabeçalho {list(df.columns)} difere do esperado {esperado}",
            )
        )
        return None
    if df.empty:
        problemas.append(Problema(nome, ERRO, "sem linhas de dados"))
        return None
    return df


def _linhas_do_csv(indices: np.ndarray) -> list[int]:
    """Converte índices do DataFrame em números de linha do arquivo (cabeçalho é a linha 1)."""
    return [int(i) + 2 for i in indices[:MAX_EXEMPLOS_NA_MENSAGEM]]


def _converter_numeros(
    df: pd.DataFrame, colunas: tuple[str, ...], nome: str, problemas: list[Problema]
) -> dict[str, np.ndarray] | None:
    """Converte colunas para float, reportando campos vazios, não numéricos e não finitos."""
    convertidas: dict[str, np.ndarray] = {}
    valido = True
    for coluna in colunas:
        bruto = df[coluna]
        vazios = (bruto.str.strip() == "").to_numpy()
        if vazios.any():
            problemas.append(
                Problema(
                    nome,
                    ERRO,
                    f"campo '{coluna}' ausente nas linhas {_linhas_do_csv(np.flatnonzero(vazios))}",
                )
            )
            valido = False
            continue

        numeros = pd.to_numeric(bruto, errors="coerce").to_numpy(dtype=float)
        ruins = ~np.isfinite(numeros)
        if ruins.any():
            exemplos = bruto.to_numpy()[ruins][:MAX_EXEMPLOS_NA_MENSAGEM].tolist()
            problemas.append(
                Problema(
                    nome,
                    ERRO,
                    f"'{coluna}' contém valores não numéricos ou não finitos nas linhas "
                    f"{_linhas_do_csv(np.flatnonzero(ruins))}: {exemplos}",
                )
            )
            valido = False
            continue

        com_espacos = (bruto != bruto.str.strip()).to_numpy()
        if com_espacos.any():
            problemas.append(
                Problema(
                    nome,
                    AVISO,
                    f"'{coluna}' tem espaços ao redor do valor nas linhas "
                    f"{_linhas_do_csv(np.flatnonzero(com_espacos))} (valor aceito sem alteração)",
                )
            )
        convertidas[coluna] = numeros
    return convertidas if valido else None


def _validar_tempos(
    tempos: np.ndarray,
    nome: str,
    problemas: list[Problema],
    minimo: int,
    rotulo: str,
) -> bool:
    """Valida quantidade mínima, origem e ordem estritamente crescente dos tempos."""
    valido = True
    if len(tempos) < minimo:
        problemas.append(
            Problema(nome, ERRO, f"{rotulo}: {len(tempos)} registro(s), mínimo {minimo}")
        )
        valido = False
    negativos = np.flatnonzero(tempos < ORIGEM_TEMPORAL_S)
    if negativos.size:
        problemas.append(
            Problema(
                nome,
                ERRO,
                f"{rotulo}: tempos anteriores à origem ({ORIGEM_TEMPORAL_S} s) nas linhas "
                f"{_linhas_do_csv(negativos)}",
            )
        )
        valido = False
    diferencas = np.diff(tempos)
    duplicados = np.flatnonzero(diferencas == 0) + 1
    if duplicados.size:
        problemas.append(
            Problema(
                nome,
                ERRO,
                f"{rotulo}: tempos duplicados nas linhas {_linhas_do_csv(duplicados)}",
            )
        )
        valido = False
    decrescentes = np.flatnonzero(diferencas < 0) + 1
    if decrescentes.size:
        problemas.append(
            Problema(
                nome,
                ERRO,
                f"{rotulo}: tempos não ordenados nas linhas {_linhas_do_csv(decrescentes)}",
            )
        )
        valido = False
    return valido


def _validar_condicoes(df: pd.DataFrame, nome: str, problemas: list[Problema]) -> dict | None:
    """Valida que há exatamente uma linha de condições, com tipos e faixas corretos."""
    if len(df) != 1:
        problemas.append(
            Problema(nome, ERRO, f"esperada exatamente 1 linha de dados; encontradas {len(df)}")
        )
        return None
    registro = df.iloc[0]
    valido = True
    for coluna in ("liquido", "dia"):
        if registro[coluna].strip() == "":
            problemas.append(Problema(nome, ERRO, f"campo '{coluna}' vazio"))
            valido = False
    numeros: dict[str, float] = {}
    for coluna in ("temperatura_c", "umidade_pct"):
        try:
            valor = float(registro[coluna])
        except ValueError:
            problemas.append(Problema(nome, ERRO, f"'{coluna}' não é numérico: {registro[coluna]!r}"))
            valido = False
            continue
        if not math.isfinite(valor):
            problemas.append(Problema(nome, ERRO, f"'{coluna}' não é finito: {registro[coluna]!r}"))
            valido = False
            continue
        numeros[coluna] = valor
    if "umidade_pct" in numeros and not 0.0 <= numeros["umidade_pct"] <= 100.0:
        problemas.append(
            Problema(nome, ERRO, f"'umidade_pct' fora de [0, 100]: {numeros['umidade_pct']}")
        )
        valido = False
    if not valido:
        return None
    return {
        "liquido": registro["liquido"],
        "dia": registro["dia"],
        "temperatura_c": numeros["temperatura_c"],
        "umidade_pct": numeros["umidade_pct"],
    }


# ---------------------------------------------------------------------------
# Validações entre arquivos
# ---------------------------------------------------------------------------


def _validar_relacoes(
    tracker: np.ndarray,
    angulo_tracker: np.ndarray,
    massa: np.ndarray,
    mergulhos: np.ndarray,
    angulo_mergulhos: np.ndarray,
    problemas: list[Problema],
) -> None:
    """Confere se os mergulhos estão no domínio dos dados e se batem com o tracker (avisos)."""
    for nome, dominio, eventos in (
        ("tracker.csv", tracker, mergulhos),
        ("massa.csv", massa, mergulhos),
    ):
        fora = np.flatnonzero((eventos < dominio.min()) | (eventos > dominio.max()))
        if fora.size:
            problemas.append(
                Problema(
                    "mergulhadas.csv",
                    AVISO,
                    f"{fora.size} mergulho(s) fora do intervalo de {nome} "
                    f"[{dominio.min():.3f}, {dominio.max():.3f}] s, "
                    f"linhas {_linhas_do_csv(fora)}",
                )
            )

    dentro = (mergulhos >= tracker.min()) & (mergulhos <= tracker.max())
    if dentro.any():
        esperado = np.interp(mergulhos[dentro], tracker, angulo_tracker)
        diferenca = np.abs(angulo_mergulhos[dentro] - esperado)
        divergentes = np.flatnonzero(diferenca > TOLERANCIA_ANGULO_EVENTO_GRAUS)
        if divergentes.size:
            indices_originais = np.flatnonzero(dentro)[divergentes]
            problemas.append(
                Problema(
                    "mergulhadas.csv",
                    AVISO,
                    f"{divergentes.size} mergulho(s) com ângulo a mais de "
                    f"{TOLERANCIA_ANGULO_EVENTO_GRAUS}° do tracker no mesmo instante; "
                    f"linhas {_linhas_do_csv(indices_originais)}",
                )
            )


# ---------------------------------------------------------------------------
# Carregamento de uma filmagem
# ---------------------------------------------------------------------------


def carregar_filmagem(pasta: Path) -> dict:
    """Lê e valida as quatro tabelas de uma filmagem, sem modificar os arquivos.

    Retorna ``id``, ``pasta``, ``tracker``, ``massa``, ``mergulhadas`` (DataFrames com
    colunas numéricas ``float``), ``condicoes`` (dicionário de uma linha) e ``avisos``
    (lista de ``Problema``).

    Levanta ``ErroFilmagem`` com todos os problemas quando há pelo menos um erro.
    """
    pasta = Path(pasta)
    problemas: list[Problema] = []

    brutos = {nome: _ler_csv(pasta, nome, problemas) for nome in ARQUIVOS_OBRIGATORIOS}

    tracker = massa = mergulhadas = condicoes = None
    if brutos["tracker.csv"] is not None:
        numeros = _converter_numeros(
            brutos["tracker.csv"], ARQUIVOS_OBRIGATORIOS["tracker.csv"], "tracker.csv", problemas
        )
        if numeros is not None and _validar_tempos(
            numeros["tempo_seg"], "tracker.csv", problemas, MIN_LINHAS_TRACKER, "tracker"
        ):
            tracker = numeros

    if brutos["massa.csv"] is not None:
        numeros = _converter_numeros(
            brutos["massa.csv"], ARQUIVOS_OBRIGATORIOS["massa.csv"], "massa.csv", problemas
        )
        if numeros is not None and _validar_tempos(
            numeros["tempo_seg"], "massa.csv", problemas, MIN_LEITURAS_AJUSTE, "massa"
        ):
            massa = numeros

    if brutos["mergulhadas.csv"] is not None:
        numeros = _converter_numeros(
            brutos["mergulhadas.csv"],
            ARQUIVOS_OBRIGATORIOS["mergulhadas.csv"],
            "mergulhadas.csv",
            problemas,
        )
        if numeros is not None and _validar_tempos(
            numeros["tempo_seg"],
            "mergulhadas.csv",
            problemas,
            MIN_MERGULHOS_PARA_PERIODO,
            "mergulhos",
        ):
            mergulhadas = numeros

    if brutos["condicoes.csv"] is not None:
        condicoes = _validar_condicoes(brutos["condicoes.csv"], "condicoes.csv", problemas)

    if tracker is not None and massa is not None and mergulhadas is not None:
        _validar_relacoes(
            tracker["tempo_seg"],
            tracker["angulo_deg"],
            massa["tempo_seg"],
            mergulhadas["tempo_seg"],
            mergulhadas["angulo_deg"],
            problemas,
        )

    if any(p.gravidade == ERRO for p in problemas) or None in (
        tracker,
        massa,
        mergulhadas,
        condicoes,
    ):
        raise ErroFilmagem(pasta, problemas)

    return {
        "id": pasta.name,
        "pasta": pasta,
        "tracker": pd.DataFrame(tracker),
        "massa": pd.DataFrame(massa),
        "mergulhadas": pd.DataFrame(mergulhadas),
        "condicoes": condicoes,
        "avisos": [p for p in problemas if p.gravidade == AVISO],
    }


# ---------------------------------------------------------------------------
# Lote com isolamento de falhas
# ---------------------------------------------------------------------------


def validar_lote(pastas: list[Path]) -> list[dict]:
    """Valida cada filmagem isoladamente; uma falha não interrompe as demais.

    Cada item tem ``id``, ``pasta``, ``status`` (``"valida"``, ``"invalida"`` ou
    ``"erro_inesperado"``), ``filmagem`` (dicionário ou ``None``) e ``problemas``.
    """
    resultados: list[dict] = []
    for pasta in pastas:
        pasta = Path(pasta)
        try:
            filmagem = carregar_filmagem(pasta)
        except ErroFilmagem as exc:
            resultados.append(
                {
                    "id": pasta.name,
                    "pasta": pasta,
                    "status": "invalida",
                    "filmagem": None,
                    "problemas": exc.problemas,
                }
            )
        except Exception as exc:  # isolamento: qualquer falha inesperada não derruba o lote
            problema = Problema(
                "(interno)", ERRO, f"erro inesperado durante a validação: {type(exc).__name__}: {exc}"
            )
            resultados.append(
                {
                    "id": pasta.name,
                    "pasta": pasta,
                    "status": "erro_inesperado",
                    "filmagem": None,
                    "problemas": [problema],
                }
            )
        else:
            resultados.append(
                {
                    "id": pasta.name,
                    "pasta": pasta,
                    "status": "valida",
                    "filmagem": filmagem,
                    "problemas": filmagem["avisos"],
                }
            )
    return resultados


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _janela_positiva(texto: str) -> float:
    try:
        valor = float(texto)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"janela deve ser numérica: {texto!r}") from exc
    if not math.isfinite(valor) or valor <= 0:
        raise argparse.ArgumentTypeError(f"janela deve ser finita e > 0: {texto!r}")
    return valor


def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m final.analisar",
        description="Valida as filmagens do pássaro bebedor. Cada subpasta de --diretorio é uma filmagem.",
    )
    parser.add_argument(
        "--diretorio",
        type=Path,
        default=DIR_DADOS_PADRAO,
        help="diretório com as subpastas de filmagem (padrão: final/dados)",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=DIR_RESULTADOS_PADRAO,
        help="diretório-base dos resultados, fora dos dados (padrão: final/resultados)",
    )
    parser.add_argument(
        "--janela",
        type=_janela_positiva,
        default=DURACAO_JANELA_PADRAO_S,
        help="duração da janela temporal em segundos (padrão: 200)",
    )
    return parser


def _dentro_de(caminho: Path, base: Path) -> bool:
    try:
        caminho.resolve().relative_to(base.resolve())
    except ValueError:
        return False
    return True


def _formatar_relatorio(resultados: list[dict]) -> list[str]:
    largura = max([len("filmagem")] + [len(item["id"]) for item in resultados]) + 2
    cabecalho = (
        f"{'filmagem':<{largura}}{'status':<18}{'massa':>7}{'mergulhos':>11}{'avisos':>8}{'erros':>7}"
    )
    linhas = [cabecalho]
    for item in resultados:
        filmagem = item["filmagem"]
        n_massa = len(filmagem["massa"]) if filmagem else "-"
        n_merg = len(filmagem["mergulhadas"]) if filmagem else "-"
        erros = sum(1 for p in item["problemas"] if p.gravidade == ERRO)
        avisos = sum(1 for p in item["problemas"] if p.gravidade == AVISO)
        linhas.append(
            f"{item['id']:<{largura}}{item['status']:<18}{str(n_massa):>7}{str(n_merg):>11}"
            f"{avisos:>8}{erros:>7}"
        )
    for item in resultados:
        if not item["problemas"]:
            continue
        linhas.append("")
        linhas.append(f"[{item['id']}]")
        for problema in item["problemas"]:
            rotulo = "ERRO" if problema.gravidade == ERRO else "aviso"
            linhas.append(f"  {rotulo}: {problema}")
    return linhas


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI. Retorna o código de saída (0, 1 ou 2)."""
    parser = _construir_parser()
    args = parser.parse_args(argv)

    if not args.diretorio.is_dir():
        print(f"erro: diretório inexistente ou não é uma pasta: {args.diretorio}", file=sys.stderr)
        return 2
    if _dentro_de(args.saida, args.diretorio):
        print(
            f"erro: --saida ({args.saida}) não pode estar dentro do diretório de dados "
            f"({args.diretorio})",
            file=sys.stderr,
        )
        return 2

    try:
        pastas = descobrir_filmagens(args.diretorio)
    except NotADirectoryError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2
    if not pastas:
        print(f"erro: nenhuma subpasta de filmagem em {args.diretorio}", file=sys.stderr)
        return 2

    resultados = validar_lote(pastas)
    for item in resultados:
        if item["status"] != "valida":
            continue
        try:
            resumo = processar_filmagem(item["filmagem"], args.janela, args.saida / item["id"])
        except Exception as exc:  # isolamento: uma falha de processamento não derruba o lote
            item["status"] = "erro_processamento"
            item["problemas"] = list(item["problemas"]) + [
                Problema("(processamento)", ERRO, f"{type(exc).__name__}: {exc}")
            ]
            continue
        item["status"] = "processada"
        item["resultado"] = resumo

    processadas = sum(1 for r in resultados if r["status"] == "processada")
    falhas = len(resultados) - processadas

    print(f"Processamento de {len(resultados)} filmagem(ns) em {args.diretorio}")
    for linha in _formatar_relatorio(resultados):
        print(linha)
    print()
    print(f"Processadas: {processadas}. Com falha: {falhas}. Janela: {args.janela:g} s. Saída: {args.saida}.")
    for item in resultados:
        if item["status"] == "processada":
            graficos = ", ".join(item["resultado"]["graficos"]) or "nenhum"
            print(f"  {item['id']}: {len(item['resultado']['arquivos'])} arquivo(s); gráficos: {graficos}")
    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
