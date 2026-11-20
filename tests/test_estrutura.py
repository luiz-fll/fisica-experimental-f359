"""Verifica que os seis módulos planejados existem e são importáveis sem efeitos colaterais."""

import importlib

import pytest

MODULOS = ["analisar", "pipeline", "periodos", "massa", "graficos", "relatorio"]


@pytest.mark.parametrize("nome", MODULOS)
def test_modulo_importavel(nome):
    assert importlib.import_module(f"final.{nome}") is not None
