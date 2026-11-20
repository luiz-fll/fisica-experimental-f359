"""Exportação de tabelas derivadas e resumos.

Preserva a precisão numérica nos arquivos: os CSVs são gravados com o valor
completo, sem arredondamento. Arredondamento ocorre só no texto de ``resumo.txt``,
para apresentação. Valores ausentes são gravados como células vazias.

Não repete cálculos: recebe tabelas e valores já prontos.

Proteção dos dados brutos: nenhuma escrita é feita dentro da pasta de origem da
filmagem (``origem``) nem sobre um arquivo que ela contém.

Funções:

- ``gravar_tabelas(pasta_saida, tabelas, origem=None) -> list[Path]``
- ``montar_resumo_texto(info: dict) -> str``
- ``gravar_resumo_texto(pasta_saida, texto, origem=None) -> Path``
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd


def _verificar_destino(destino: Path, origem: Path | None) -> None:
    if origem is None:
        return
    origem_resolvida = Path(origem).resolve()
    destino_resolvido = destino.resolve()
    if destino_resolvido == origem_resolvida or origem_resolvida in destino_resolvido.parents:
        raise PermissionError(f"saída não pode ser gravada dentro da pasta de dados: {destino}")
    alvo = origem_resolvida / destino.name
    if alvo.exists() and alvo.resolve() == destino_resolvido:
        raise PermissionError(f"saída colidiria com um arquivo de dados: {alvo}")


def gravar_tabelas(
    pasta_saida: Path,
    tabelas: dict[str, pd.DataFrame],
    origem: Path | None = None,
) -> list[Path]:
    """Grava cada tabela como CSV em ``pasta_saida`` com precisão completa.

    ``tabelas`` mapeia o nome do arquivo (por exemplo ``periodos.csv``) ao DataFrame.
    Cria a pasta se necessário. Sobrescreve apenas os arquivos de mesmo nome, que são
    saídas derivadas de execuções anteriores.
    """
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    gravados: list[Path] = []
    for nome, tabela in tabelas.items():
        destino = pasta_saida / nome
        _verificar_destino(destino, origem)
        tabela.to_csv(destino, index=False)
        gravados.append(destino)
    return gravados


def _formatar(valor, casas: int = 6) -> str:
    if valor is None:
        return "ausente"
    if isinstance(valor, bool):
        return "sim" if valor else "não"
    if isinstance(valor, float):
        if math.isnan(valor):
            return "ausente"
        return f"{valor:.{casas}g}"
    return str(valor)


def montar_resumo_texto(info: dict) -> str:
    """Monta o texto de ``resumo.txt`` a partir de valores já calculados.

    Chaves esperadas em ``info``: ``id``, ``condicoes``, ``t_fim_s``, ``duracao_janela_s``,
    ``n_janelas``, ``n_mergulhos``, ``periodos`` (estatísticas), ``n_ciclos_sem_suporte``,
    ``massa`` (ajuste global), ``avisos`` (lista de textos), ``graficos`` (lista de nomes
    gerados) e ``graficos_omitidos`` (lista de pares nome, motivo).
    """
    cond = info["condicoes"]
    per = info["periodos"]
    mas = info["massa"]
    linhas: list[str] = []
    linhas.append(f"Resumo da filmagem {info['id']}")
    linhas.append("=" * (len("Resumo da filmagem ") + len(info["id"])))
    linhas.append("")
    linhas.append("Condições (constantes adotadas para o ensaio, um registro por filmagem)")
    linhas.append(f"  líquido: {cond['liquido']}; dia: {cond['dia']}")
    linhas.append(f"  temperatura: {_formatar(cond['temperatura_c'])} °C; umidade: {_formatar(cond['umidade_pct'])} %")
    linhas.append("")
    linhas.append("Ensaio")
    linhas.append(f"  instante final considerado: {_formatar(info['t_fim_s'])} s")
    linhas.append(f"  janelas de {_formatar(info['duracao_janela_s'])} s: {info['n_janelas']}")
    linhas.append(f"  mergulhos anotados: {info['n_mergulhos']}")
    linhas.append("")
    linhas.append("Períodos (intervalos entre mergulhos consecutivos)")
    linhas.append(f"  ciclos: {per['n']} (sem massa interpolada: {info['n_ciclos_sem_suporte']})")
    if per["n"] == 0:
        linhas.append("  sem ciclos: não há estatísticas de período.")
    else:
        linhas.append(f"  média: {_formatar(per['media_s'])} s")
        linhas.append(f"  desvio-padrão amostral: {_formatar(per['desvio_padrao_s'])} s")
        linhas.append(f"  mínimo: {_formatar(per['minimo_s'])} s; máximo: {_formatar(per['maximo_s'])} s")
        if per["n"] < 2:
            linhas.append("  desvio-padrão ausente: é necessário ao menos 2 ciclos.")
    linhas.append("")
    linhas.append("Massa (ajuste linear global m(t) = a + b·t)")
    linhas.append(f"  leituras: {mas['n_leituras']}; status: {mas['status']}")
    if mas["status"] == "ok":
        linhas.append(f"  b = {_formatar(mas['b_g_s'])} g/s")
        if mas["tipo_taxa"] == "perda":
            linhas.append(
                f"  taxa positiva de perda: {_formatar(mas['taxa_g_s'])} g/s "
                f"({_formatar(mas['taxa_g_min'])} g/min)"
            )
        else:
            linhas.append("  inclinação não negativa: não é reportada como taxa de evaporação.")
        linhas.append(f"  R² (diagnóstico auxiliar): {_formatar(mas['r2'])}")
        linhas.append(f"  erro padrão de b: {_formatar(mas['erro_padrao_b_g_s'])} g/s")
        linhas.append(f"  resíduo máximo absoluto: {_formatar(mas['residuo_max_abs_g'])} g")
    if mas.get("diagnosticos"):
        linhas.append(f"  diagnósticos: {mas['diagnosticos']}")
    linhas.append("")
    linhas.append("Avisos de validação")
    if info["avisos"]:
        linhas.extend(f"  - {aviso}" for aviso in info["avisos"])
    else:
        linhas.append("  nenhum")
    linhas.append("")
    linhas.append("Gráficos")
    if info["graficos"]:
        linhas.extend(f"  gerado: {nome}" for nome in info["graficos"])
    for nome, motivo in info["graficos_omitidos"]:
        linhas.append(f"  omitido: {nome} — {motivo}")
    linhas.append("")
    linhas.append("Limitações")
    linhas.append("  Resultados são estimativas e diagnósticos. Não são uma verificação da hipótese física.")
    linhas.append("  O R² é auxiliar; a adequação do ajuste depende dos resíduos e do contexto experimental.")
    linhas.append("  As condições ambientais são um único registro por filmagem; não há série temporal.")
    return "\n".join(linhas) + "\n"


def gravar_resumo_texto(
    pasta_saida: Path,
    texto: str,
    origem: Path | None = None,
) -> Path:
    """Grava ``resumo.txt`` em ``pasta_saida``, com as mesmas proteções de ``gravar_tabelas``."""
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    destino = pasta_saida / "resumo.txt"
    _verificar_destino(destino, origem)
    destino.write_text(texto, encoding="utf-8")
    return destino
