"""Verifica que os mínimos e a origem temporal documentados estão definidos nos módulos."""

from final import massa, periodos


def test_origem_temporal_e_duracao_padrao_documentadas():
    assert periodos.ORIGEM_TEMPORAL_S == 0.0
    assert periodos.DURACAO_JANELA_PADRAO_S == 200.0


def test_minimos_de_periodos():
    assert periodos.MIN_MERGULHOS_PARA_PERIODO == 2
    assert periodos.MIN_PERIODOS_PARA_DESVIO == 2


def test_minimos_de_ajuste_de_massa():
    assert massa.MIN_LEITURAS_AJUSTE == 3
    assert massa.LEITURAS_RECOMENDADAS_AJUSTE == 5
    assert massa.LEITURAS_RECOMENDADAS_AJUSTE >= massa.MIN_LEITURAS_AJUSTE
