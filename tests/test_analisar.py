"""Testes da leitura, validação, isolamento de lote e CLI (final/analisar.py).

As filmagens são sintéticas e criadas em diretórios temporários. Os testes nunca
modificam os dados reais.
"""

import hashlib
import math
from pathlib import Path

import pytest

from final import analisar
from final.analisar import (
    ERRO,
    AVISO,
    ErroFilmagem,
    carregar_filmagem,
    descobrir_filmagens,
    main,
    validar_lote,
)

CABECALHO_TRACKER = "tempo_seg,angulo_deg"
CABECALHO_MASSA = "tempo_seg,massa_g"
CABECALHO_MERGULHOS = "tempo_seg,angulo_deg"
CABECALHO_CONDICOES = "liquido,dia,temperatura_c,umidade_pct"
LINHA_CONDICOES = "agua,2026-10-19,23.4,53"


def angulo_sintetico(t: float) -> float:
    return 10.0 + 5.0 * math.sin(t)


def conteudo_padrao() -> dict[str, str]:
    """Filmagem válida mínima: tracker 0–20 s, massa 0–50 s, três mergulhos concordantes."""
    tracker = [CABECALHO_TRACKER]
    for i in range(41):
        t = i * 0.5
        tracker.append(f"{t:.3f},{angulo_sintetico(t):.6f}")
    massa = [CABECALHO_MASSA] + [f"{5.0 * i:.3f},{41.0 - 0.01 * 5.0 * i:.4f}" for i in range(11)]
    mergulhos = [CABECALHO_MERGULHOS] + [
        f"{t:.3f},{angulo_sintetico(t):.6f}" for t in (2.0, 8.0, 14.0)
    ]
    return {
        "tracker.csv": "\n".join(tracker) + "\n",
        "massa.csv": "\n".join(massa) + "\n",
        "mergulhadas.csv": "\n".join(mergulhos) + "\n",
        "condicoes.csv": f"{CABECALHO_CONDICOES}\n{LINHA_CONDICOES}\n",
    }


def criar_filmagem(base: Path, nome: str, alteracoes: dict[str, str] | None = None) -> Path:
    pasta = base / nome
    pasta.mkdir(parents=True)
    conteudo = conteudo_padrao()
    for arquivo, texto in (alteracoes or {}).items():
        if texto is None:
            conteudo.pop(arquivo, None)
        else:
            conteudo[arquivo] = texto
    for arquivo, texto in conteudo.items():
        (pasta / arquivo).write_bytes(texto.encode("utf-8"))
    return pasta


def mensagens(exc: ErroFilmagem) -> str:
    return " | ".join(str(p) for p in exc.problemas)


def erros_de(pasta: Path) -> str:
    with pytest.raises(ErroFilmagem) as info:
        carregar_filmagem(pasta)
    return mensagens(info.value)


def hash_arquivos(pasta: Path) -> dict[str, str]:
    return {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(pasta.iterdir())
    }


# ---------------------------------------------------------------------------
# Filmagem válida
# ---------------------------------------------------------------------------


def test_filmagem_valida_carrega_com_contrato(tmp_path):
    pasta = criar_filmagem(tmp_path, "agua_teste")
    filmagem = carregar_filmagem(pasta)
    assert filmagem["id"] == "agua_teste"
    assert filmagem["pasta"] == pasta
    assert list(filmagem["tracker"].columns) == ["tempo_seg", "angulo_deg"]
    assert list(filmagem["massa"].columns) == ["tempo_seg", "massa_g"]
    assert list(filmagem["mergulhadas"].columns) == ["tempo_seg", "angulo_deg"]
    assert filmagem["condicoes"] == {
        "liquido": "agua",
        "dia": "2026-10-19",
        "temperatura_c": 23.4,
        "umidade_pct": 53.0,
    }
    assert filmagem["avisos"] == []
    assert filmagem["tracker"]["tempo_seg"].dtype == float


def test_leitura_nao_modifica_arquivos(tmp_path):
    pasta = criar_filmagem(tmp_path, "agua_teste")
    antes = hash_arquivos(pasta)
    carregar_filmagem(pasta)
    assert hash_arquivos(pasta) == antes


def test_trk_nunca_e_lido(tmp_path):
    pasta = criar_filmagem(tmp_path, "agua_teste")
    (pasta / "agua_teste.trk").write_bytes(b"\x00\xff nao e xml")
    assert carregar_filmagem(pasta)["id"] == "agua_teste"


def test_bom_e_crlf_sao_aceitos(tmp_path):
    texto = {
        k: "\ufeff" + v.replace("\n", "\r\n") for k, v in conteudo_padrao().items()
    }
    pasta = tmp_path / "bom_crlf"
    pasta.mkdir()
    for arquivo, conteudo in texto.items():
        (pasta / arquivo).write_bytes(conteudo.encode("utf-8"))
    assert carregar_filmagem(pasta)["condicoes"]["liquido"] == "agua"


# ---------------------------------------------------------------------------
# Arquivos e cabeçalhos
# ---------------------------------------------------------------------------


def test_arquivo_ausente_e_identificado(tmp_path):
    pasta = criar_filmagem(tmp_path, "sem_massa", {"massa.csv": None})
    assert "massa.csv: arquivo ausente" in erros_de(pasta)


def test_cabecalho_com_typo_e_rejeitado(tmp_path):
    pasta = criar_filmagem(
        tmp_path, "typo", {"massa.csv": "temp_seg,massa_g\n0.0,41.0\n5.0,40.9\n10.0,40.8\n"}
    )
    texto = erros_de(pasta)
    assert "massa.csv" in texto and "temp_seg" in texto and "tempo_seg" in texto


def test_cabecalho_com_coluna_extra_e_rejeitado(tmp_path):
    pasta = criar_filmagem(tmp_path, "extra", {"massa.csv": "tempo_seg,massa_g,extra\n0.0,41.0,1\n5.0,40.9,1\n10.0,40.8,1\n"})
    assert "difere do esperado" in erros_de(pasta)


def test_arquivo_vazio_e_rejeitado(tmp_path):
    pasta = criar_filmagem(tmp_path, "vazio", {"tracker.csv": ""})
    assert "arquivo vazio" in erros_de(pasta)


def test_cabecalho_sem_linhas_de_dados(tmp_path):
    pasta = criar_filmagem(tmp_path, "sem_linhas", {"massa.csv": CABECALHO_MASSA + "\n"})
    assert "sem linhas de dados" in erros_de(pasta)


def test_numero_de_campos_inconsistente(tmp_path):
    pasta = criar_filmagem(
        tmp_path, "campos", {"massa.csv": "tempo_seg,massa_g\n0.0,41.0\n5.0,40.9,9\n10.0,40.8\n"}
    )
    assert "número de campos inconsistente" in erros_de(pasta)


def test_arquivo_nao_utf8(tmp_path):
    pasta = criar_filmagem(tmp_path, "latin1")
    (pasta / "massa.csv").write_bytes("tempo_seg,massa_g\n0.0,41.0\n5.0,40,9\n10.0,é\n".encode("latin-1"))
    assert "não está codificado em UTF-8" in erros_de(pasta)


# ---------------------------------------------------------------------------
# Valores
# ---------------------------------------------------------------------------


def test_valor_malformado_identifica_linha(tmp_path):
    pasta = criar_filmagem(
        tmp_path,
        "malformado",
        {"massa.csv": "tempo_seg,massa_g\n0.0,41.0\n600.007.41.4779,\n10.0,40.8\n"},
    )
    texto = erros_de(pasta)
    assert "massa.csv" in texto
    assert "[3]" in texto  # a linha 1 é o cabeçalho; a linha malformada é a 3


def test_campo_vazio_e_identificado_como_ausente(tmp_path):
    pasta = criar_filmagem(
        tmp_path, "vazio_campo", {"massa.csv": "tempo_seg,massa_g\n0.0,41.0\n5.0,\n10.0,40.8\n"}
    )
    assert "campo 'massa_g' ausente nas linhas [3]" in erros_de(pasta)


@pytest.mark.parametrize("valor", ["nan", "inf", "-inf", "abc"])
def test_valores_nao_finitos_ou_textuais_sao_erro(tmp_path, valor):
    pasta = criar_filmagem(
        tmp_path, f"valor_{valor.replace('-', 'm')}", {"massa.csv": f"tempo_seg,massa_g\n0.0,41.0\n5.0,{valor}\n10.0,40.8\n"}
    )
    assert "não numéricos ou não finitos" in erros_de(pasta)


def test_espacos_ao_redor_do_valor_geram_aviso_sem_alterar(tmp_path):
    pasta = criar_filmagem(
        tmp_path, "espacos", {"massa.csv": "tempo_seg,massa_g\n0.0, 41.0\n5.0,40.9\n10.0,40.8\n"}
    )
    filmagem = carregar_filmagem(pasta)
    assert filmagem["massa"]["massa_g"].tolist() == [41.0, 40.9, 40.8]
    assert any("espaços ao redor" in str(p) for p in filmagem["avisos"])


def test_tempos_duplicados_sao_erro(tmp_path):
    pasta = criar_filmagem(
        tmp_path, "duplicado", {"massa.csv": "tempo_seg,massa_g\n0.0,41.0\n5.0,40.9\n5.0,40.8\n10.0,40.7\n"}
    )
    assert "tempos duplicados nas linhas [4]" in erros_de(pasta)


def test_tempos_nao_ordenados_sao_erro(tmp_path):
    pasta = criar_filmagem(
        tmp_path, "desordem", {"massa.csv": "tempo_seg,massa_g\n0.0,41.0\n10.0,40.9\n5.0,40.8\n15.0,40.7\n"}
    )
    assert "tempos não ordenados nas linhas [4]" in erros_de(pasta)


def test_tempo_negativo_e_erro(tmp_path):
    pasta = criar_filmagem(
        tmp_path, "negativo", {"massa.csv": "tempo_seg,massa_g\n-1.0,41.0\n5.0,40.9\n10.0,40.8\n"}
    )
    assert "anteriores à origem" in erros_de(pasta)


def test_massa_com_leituras_insuficientes(tmp_path):
    pasta = criar_filmagem(tmp_path, "poucas", {"massa.csv": "tempo_seg,massa_g\n0.0,41.0\n5.0,40.9\n"})
    assert "massa: 2 registro(s), mínimo 3" in erros_de(pasta)


def test_tracker_com_um_unico_registro(tmp_path):
    pasta = criar_filmagem(tmp_path, "tracker_curto", {"tracker.csv": "tempo_seg,angulo_deg\n0.0,10.0\n"})
    assert "tracker: 1 registro(s), mínimo 2" in erros_de(pasta)


def test_mergulho_unico_nao_permite_periodo(tmp_path):
    pasta = criar_filmagem(
        tmp_path, "um_mergulho", {"mergulhadas.csv": "tempo_seg,angulo_deg\n8.0,10.0\n"}
    )
    assert "mergulhos: 1 registro(s), mínimo 2" in erros_de(pasta)


def test_mergulho_duplicado_e_erro(tmp_path):
    pasta = criar_filmagem(
        tmp_path,
        "mergulho_dup",
        {"mergulhadas.csv": "tempo_seg,angulo_deg\n2.0,10.0\n2.0,10.0\n8.0,10.0\n"},
    )
    assert "mergulhos: tempos duplicados" in erros_de(pasta)


# ---------------------------------------------------------------------------
# Condições
# ---------------------------------------------------------------------------


def test_condicoes_sem_linha_de_dados(tmp_path):
    pasta = criar_filmagem(tmp_path, "cond0", {"condicoes.csv": CABECALHO_CONDICOES + "\n"})
    assert "sem linhas de dados" in erros_de(pasta)


def test_condicoes_com_duas_linhas(tmp_path):
    pasta = criar_filmagem(
        tmp_path,
        "cond2",
        {"condicoes.csv": f"{CABECALHO_CONDICOES}\n{LINHA_CONDICOES}\n{LINHA_CONDICOES}\n"},
    )
    assert "esperada exatamente 1 linha" in erros_de(pasta)


def test_umidade_fora_do_intervalo(tmp_path):
    pasta = criar_filmagem(
        tmp_path, "umid", {"condicoes.csv": f"{CABECALHO_CONDICOES}\nagua,2026-10-19,23.4,120\n"}
    )
    assert "'umidade_pct' fora de [0, 100]" in erros_de(pasta)


def test_temperatura_nao_numerica(tmp_path):
    pasta = criar_filmagem(
        tmp_path, "temp", {"condicoes.csv": f"{CABECALHO_CONDICOES}\nagua,2026-10-19,quente,53\n"}
    )
    assert "'temperatura_c' não é numérico" in erros_de(pasta)


def test_liquido_vazio(tmp_path):
    pasta = criar_filmagem(
        tmp_path, "liq", {"condicoes.csv": f"{CABECALHO_CONDICOES}\n ,2026-10-19,23.4,53\n"}
    )
    assert "campo 'liquido' vazio" in erros_de(pasta)


# ---------------------------------------------------------------------------
# Relações entre arquivos
# ---------------------------------------------------------------------------


def test_mergulho_fora_do_intervalo_do_tracker_gera_aviso(tmp_path):
    pasta = criar_filmagem(
        tmp_path,
        "fora_tracker",
        {"mergulhadas.csv": "tempo_seg,angulo_deg\n2.0,10.0\n8.0,10.0\n99.0,10.0\n"},
    )
    filmagem = carregar_filmagem(pasta)
    assert any("fora do intervalo de tracker.csv" in str(p) for p in filmagem["avisos"])


def test_mergulho_fora_do_intervalo_da_massa_gera_aviso(tmp_path):
    pasta = criar_filmagem(
        tmp_path,
        "fora_massa",
        {"mergulhadas.csv": "tempo_seg,angulo_deg\n2.0,10.0\n8.0,10.0\n60.0,10.0\n"},
    )
    filmagem = carregar_filmagem(pasta)
    assert any("fora do intervalo de massa.csv" in str(p) for p in filmagem["avisos"])


def test_angulo_do_mergulho_divergente_do_tracker_gera_aviso(tmp_path):
    pasta = criar_filmagem(
        tmp_path,
        "divergente",
        {"mergulhadas.csv": "tempo_seg,angulo_deg\n2.0,70.8\n8.0,10.0\n14.0,10.0\n"},
    )
    filmagem = carregar_filmagem(pasta)
    assert any("a mais de 2.0° do tracker" in str(p) for p in filmagem["avisos"])


def test_erros_de_varios_arquivos_sao_reportados_juntos(tmp_path):
    pasta = criar_filmagem(
        tmp_path,
        "multi",
        {
            "massa.csv": "tempo_seg,massa_g\n0.0,41.0\n",
            "condicoes.csv": f"{CABECALHO_CONDICOES}\n",
        },
    )
    with pytest.raises(ErroFilmagem) as info:
        carregar_filmagem(pasta)
    arquivos = {p.arquivo for p in info.value.erros}
    assert {"massa.csv", "condicoes.csv"} <= arquivos


# ---------------------------------------------------------------------------
# Descoberta e lote
# ---------------------------------------------------------------------------


def test_descoberta_ignora_arquivos_e_pastas_ocultas(tmp_path):
    criar_filmagem(tmp_path, "b_filmagem")
    criar_filmagem(tmp_path, "a_filmagem")
    (tmp_path / "solto.txt").write_text("x")
    (tmp_path / ".oculta").mkdir()
    nomes = [p.name for p in descobrir_filmagens(tmp_path)]
    assert nomes == ["a_filmagem", "b_filmagem"]


def test_descoberta_de_diretorio_inexistente(tmp_path):
    with pytest.raises(NotADirectoryError):
        descobrir_filmagens(tmp_path / "nao_existe")


def test_lote_isola_filmagem_invalida(tmp_path):
    a = criar_filmagem(tmp_path, "a_ok")
    b = criar_filmagem(tmp_path, "b_ruim", {"massa.csv": None})
    c = criar_filmagem(tmp_path, "c_ok")
    resultados = validar_lote([a, b, c])
    assert [r["status"] for r in resultados] == ["valida", "invalida", "valida"]
    assert resultados[1]["filmagem"] is None
    assert resultados[2]["filmagem"]["id"] == "c_ok"


def test_lote_continua_apos_falha_inesperada(tmp_path, monkeypatch):
    a = criar_filmagem(tmp_path, "a_ok")
    b = criar_filmagem(tmp_path, "b_explode")
    c = criar_filmagem(tmp_path, "c_ok")
    original = analisar.carregar_filmagem

    def falha_seletiva(pasta):
        if pasta.name == "b_explode":
            raise RuntimeError("falha simulada")
        return original(pasta)

    monkeypatch.setattr(analisar, "carregar_filmagem", falha_seletiva)
    resultados = validar_lote([a, b, c])
    assert [r["status"] for r in resultados] == ["valida", "erro_inesperado", "valida"]
    assert "falha simulada" in str(resultados[1]["problemas"][0])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_todas_validas_retorna_zero(tmp_path, capsys):
    criar_filmagem(tmp_path / "dados", "a_ok")
    criar_filmagem(tmp_path / "dados", "b_ok")
    codigo = main(["--diretorio", str(tmp_path / "dados"), "--saida", str(tmp_path / "res")])
    saida = capsys.readouterr().out
    assert codigo == 0
    assert "Processadas: 2. Com falha: 0." in saida
    assert (tmp_path / "res" / "a_ok" / "resumo.txt").is_file()
    assert (tmp_path / "res" / "b_ok" / "resumo.txt").is_file()


def test_cli_com_filmagem_invalida_retorna_um_e_identifica_arquivo(tmp_path, capsys):
    criar_filmagem(tmp_path / "dados", "a_ok")
    criar_filmagem(tmp_path / "dados", "b_ruim", {"massa.csv": None})
    codigo = main(["--diretorio", str(tmp_path / "dados"), "--saida", str(tmp_path / "res")])
    saida = capsys.readouterr().out
    assert codigo == 1
    assert "[b_ruim]" in saida and "massa.csv: arquivo ausente" in saida
    assert "Processadas: 1. Com falha: 1." in saida


def test_cli_diretorio_inexistente_retorna_dois(tmp_path, capsys):
    codigo = main(["--diretorio", str(tmp_path / "nao_existe"), "--saida", str(tmp_path / "res")])
    assert codigo == 2
    assert "inexistente" in capsys.readouterr().err


def test_cli_saida_dentro_dos_dados_retorna_dois(tmp_path, capsys):
    dados = tmp_path / "dados"
    criar_filmagem(dados, "a_ok")
    codigo = main(["--diretorio", str(dados), "--saida", str(dados / "resultados")])
    assert codigo == 2
    assert "não pode estar dentro" in capsys.readouterr().err


def test_cli_sem_subpastas_retorna_dois(tmp_path, capsys):
    (tmp_path / "vazio").mkdir()
    codigo = main(["--diretorio", str(tmp_path / "vazio"), "--saida", str(tmp_path / "res")])
    assert codigo == 2
    assert "nenhuma subpasta" in capsys.readouterr().err


@pytest.mark.parametrize("janela", ["0", "-5", "nan", "inf", "abc"])
def test_cli_janela_invalida_e_erro_de_uso(tmp_path, janela, capsys):
    criar_filmagem(tmp_path / "dados", "a_ok")
    with pytest.raises(SystemExit) as info:
        main(["--diretorio", str(tmp_path / "dados"), "--saida", str(tmp_path / "res"), "--janela", janela])
    assert info.value.code == 2


def test_cli_janela_valida_aparece_no_resumo(tmp_path, capsys):
    criar_filmagem(tmp_path / "dados", "a_ok")
    main(["--diretorio", str(tmp_path / "dados"), "--saida", str(tmp_path / "res"), "--janela", "150"])
    assert "Janela: 150 s" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Processamento em lote pela CLI
# ---------------------------------------------------------------------------


def test_cli_grava_resultados_fora_dos_dados(tmp_path):
    dados = tmp_path / "dados"
    criar_filmagem(dados, "a_ok")
    saida = tmp_path / "res"
    assert main(["--diretorio", str(dados), "--saida", str(saida)]) == 0
    esperados = {
        "periodos.csv", "massa_ajuste.csv", "massa_residuos.csv",
        "massa_por_janela.csv", "periodo_por_janela.csv", "resumo.csv", "resumo.txt",
    }
    assert esperados <= {p.name for p in (saida / "a_ok").iterdir()}


def test_cli_falha_de_processamento_nao_interrompe_o_lote(tmp_path, monkeypatch, capsys):
    criar_filmagem(tmp_path / "dados", "a_explode")
    criar_filmagem(tmp_path / "dados", "b_ok")
    original = analisar.processar_filmagem

    def falha_seletiva(filmagem, janela, saida):
        if filmagem["id"] == "a_explode":
            raise RuntimeError("falha de cálculo simulada")
        return original(filmagem, janela, saida)

    monkeypatch.setattr(analisar, "processar_filmagem", falha_seletiva)
    codigo = main(["--diretorio", str(tmp_path / "dados"), "--saida", str(tmp_path / "res")])
    saida = capsys.readouterr().out
    assert codigo == 1
    assert "Processadas: 1. Com falha: 1." in saida
    assert "falha de cálculo simulada" in saida
    assert (tmp_path / "res" / "b_ok" / "resumo.txt").is_file()


def test_liquido_desconhecido_e_erro_identificado(tmp_path):
    pasta = criar_filmagem(
        tmp_path, "liq_desc", {"condicoes.csv": f"{CABECALHO_CONDICOES}\nvinho,2026-10-19,23.4,53\n"}
    )
    texto = erros_de(pasta)
    assert "condicoes.csv" in texto and "'liquido' desconhecido" in texto and "vinho" in texto
