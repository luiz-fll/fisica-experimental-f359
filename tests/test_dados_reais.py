"""Validação somente leitura dos conjuntos reais em final/dados/.

Não modifica nenhum arquivo. Ignorado quando a pasta não existe.
"""

import pytest

from final import analisar

pytestmark = pytest.mark.skipif(
    not analisar.DIR_DADOS_PADRAO.is_dir(), reason="final/dados ausente"
)


def test_dados_reais_sao_validos_sem_erros():
    pastas = analisar.descobrir_filmagens(analisar.DIR_DADOS_PADRAO)
    assert len(pastas) == 9
    resultados = analisar.validar_lote(pastas)
    invalidas = [(r["id"], [str(p) for p in r["problemas"]]) for r in resultados if r["status"] != "valida"]
    assert invalidas == []


def test_calculos_sobre_dados_reais_sao_consistentes_entre_janelas():
    """Cada filmagem gera n-1 ciclos, e nenhum ciclo ou leitura se perde ao agregar por janela."""
    from final.massa import ajustar_janelas, ajustar_linear
    from final.periodos import construir_ciclos, definir_limites_janelas, periodos_por_janela

    pastas = analisar.descobrir_filmagens(analisar.DIR_DADOS_PADRAO)
    for resultado in analisar.validar_lote(pastas):
        assert resultado["status"] == "valida", resultado["id"]
        filmagem = resultado["filmagem"]
        massa = filmagem["massa"]
        mergulhos = filmagem["mergulhadas"]

        ciclos = construir_ciclos(mergulhos, massa)
        assert len(ciclos) == len(mergulhos) - 1, resultado["id"]

        t_fim = float(max(massa["tempo_seg"].max(), mergulhos["tempo_seg"].max()))
        limites = definir_limites_janelas(t_fim)

        por_janela = periodos_por_janela(ciclos, limites)
        ciclos_no_dominio = int(ciclos["ponto_medio_s"].between(0.0, t_fim).sum())
        assert int(por_janela["n_ciclos"].sum()) == ciclos_no_dominio, resultado["id"]

        ajuste_janelas = ajustar_janelas(massa, limites)
        assert int(ajuste_janelas["n_leituras"].sum()) == len(massa), resultado["id"]

        global_ = ajustar_linear(massa["tempo_seg"].to_numpy(), massa["massa_g"].to_numpy())
        assert global_["status"] == "ok", resultado["id"]
