"""Adyacencia de la red real (R2, caso 15). Necesita data/processed/ (se salta si falta)."""
import math

import pytest

from rutas.r2.adyacencia import construir_adyacencia

pytestmark = pytest.mark.red


def test_caso_15_adyacencia_real(grafo_procesado_real):
    G = grafo_procesado_real
    red = construir_adyacencia(G)
    V = 8791
    assert len(red.ids) == len(red.adyacencia) == V
    assert red.ids == sorted(G.nodes)
    assert all(red.indice[red.ids[i]] == i for i in range(V))
    assert sum(len(vecinos) for vecinos in red.adyacencia) == 20132
    for vecinos in red.adyacencia:
        for j, tiempo in vecinos:
            assert 0 <= j < V
            assert math.isfinite(tiempo) and tiempo >= 0
