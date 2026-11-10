"""Pruebas de rutas/r1/componente.py (casos 5 y 6)."""
import networkx as nx

from rutas.r1.componente import contar, obtener_componente
from tests.conftest import grafo_sintetico

NODOS = {n: (-75.6 - 0.01 * i, 4.5) for i, n in enumerate("ABCDE")}


def test_caso_5_componente_abc():
    G = grafo_sintetico(NODOS, [("A", "B", {}), ("B", "C", {}), ("C", "A", {}),
                                ("C", "D", {}), ("D", "E", {})])
    comp = obtener_componente(G)
    assert contar(comp) == (3, 3)
    esperado = max(nx.strongly_connected_components(G), key=len)
    assert set(comp.nodes) == esperado == {"A", "B", "C"}


def test_caso_6_ya_fuertemente_conexa():
    G = grafo_sintetico(NODOS, [("A", "B", {}), ("B", "C", {}), ("C", "A", {})])
    comp = obtener_componente(G)
    assert contar(comp) == (3, 3)
    assert set(comp.nodes) == {"A", "B", "C"}


def test_contar_incluye_paralelas():
    nodos = {n: NODOS[n] for n in "AB"}
    G = grafo_sintetico(nodos, [("A", "B", 0, {}), ("A", "B", 1, {}), ("B", "A", 0, {})])
    assert contar(G) == (2, 3)
    assert contar(obtener_componente(G)) == (2, 3)
