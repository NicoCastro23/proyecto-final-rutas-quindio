"""Pruebas de la representación indexada (R2, casos 8, 9 y 12)."""
import math

import networkx as nx
import pytest

from rutas.r2.adyacencia import construir_adyacencia
from tests.conftest import grafo_sintetico, red_desde_aristas

# G1 de la spec con A=1 ... F=6 (F aislado)
G1 = [(1, 2, 4), (1, 3, 1), (3, 2, 2), (2, 4, 1), (3, 4, 5), (4, 5, 3)]


def test_g1_red_indexada():
    red = red_desde_aristas(G1, nodos=[6])
    assert red.ids == [1, 2, 3, 4, 5, 6]
    assert all(red.indice[k] == k - 1 for k in range(1, 7))
    assert len(red.adyacencia) == 6
    assert red.adyacencia[5] == []
    assert sum(len(a) for a in red.adyacencia) == 6
    assert (1, 4.0) in red.adyacencia[0] and (2, 1.0) in red.adyacencia[0]


def test_ids_ordenados_e_indice():
    G = nx.MultiDiGraph()
    for n in (30, 10, 20):
        G.add_node(n)
    G.add_edge(30, 10, travel_time=7.0)
    G.add_edge(10, 20, travel_time=9.0)
    red = construir_adyacencia(G)
    assert red.ids == [10, 20, 30]
    assert red.indice == {10: 0, 20: 1, 30: 2}
    assert red.adyacencia[2] == [(0, 7.0)]
    assert red.adyacencia[0] == [(1, 9.0)]


def _multigrafo_caso_12():
    nodos = {1: (-75.6, 4.5), 2: (-75.7, 4.6)}
    return grafo_sintetico(nodos, [
        (1, 2, 0, {"travel_time": 50.0, "length": 800.0}),
        (1, 2, 1, {"travel_time": 40.0, "length": 900.0}),
        (1, 1, 0, {"travel_time": 5.0, "length": 10.0}),
        (2, 1, 0, {"travel_time": 10.0, "length": 700.0}),
    ])


def test_paralelas_y_autolazo_se_conservan():
    red = construir_adyacencia(_multigrafo_caso_12())
    assert (1, 50.0) in red.adyacencia[0]
    assert (1, 40.0) in red.adyacencia[0]
    assert (0, 5.0) in red.adyacencia[0]
    assert sum(len(a) for a in red.adyacencia) == 4


def test_peso_cero_permitido():
    red = red_desde_aristas([(1, 2, 0.0)])
    assert red.adyacencia[0] == [(1, 0.0)]


@pytest.mark.parametrize("malo", [-1, float("nan"), math.inf])
def test_caso_9_peso_invalido(malo):
    G = nx.MultiDiGraph()
    G.add_edge(10, 20, key=3, travel_time=malo)
    with pytest.raises(ValueError) as e:
        construir_adyacencia(G)
    mensaje = str(e.value)
    assert "10" in mensaje and "20" in mensaje and "3" in mensaje
