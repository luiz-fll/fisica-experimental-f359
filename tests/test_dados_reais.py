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
