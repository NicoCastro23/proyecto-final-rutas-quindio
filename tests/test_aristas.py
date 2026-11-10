"""Pruebas de rutas/r1/aristas.py (caso 11b)."""
import pytest
from shapely.geometry import LineString

from rutas.r1.aristas import AristaElegida, mejor_arista
from tests.conftest import grafo_sintetico

NODOS = {"A": (-75.67, 4.53), "B": (-75.66, 4.54)}
CURVA = LineString([(-75.67, 4.53), (-75.665, 4.538), (-75.66, 4.54)])


def grafo_paralelas():
    """A -> B con clave 0 (50 s, 800 m) y clave 1 (40 s, 900 m, geometría propia)."""
    return grafo_sintetico(NODOS, [
        ("A", "B", 0, {"length": 800.0, "travel_time": 50.0}),
        ("A", "B", 1, {"length": 900.0, "travel_time": 40.0, "geometry": CURVA}),
    ])


def test_caso_11b_menor_tiempo():
    e = mejor_arista(grafo_paralelas(), "A", "B")
    assert isinstance(e, AristaElegida)
    assert (e.u, e.v, e.key) == ("A", "B", 1)
    assert e.travel_time == 40.0 and e.length == 900.0
    assert e.geometry.equals(CURVA)


def test_caso_11b_empate_menor_key():
    G = grafo_sintetico(NODOS, [
        ("A", "B", 3, {"length": 700.0, "travel_time": 40.0}),
        ("A", "B", 1, {"length": 900.0, "travel_time": 40.0}),
        ("A", "B", 2, {"length": 800.0, "travel_time": 60.0}),
    ])
    e = mejor_arista(G, "A", "B")
    assert e.key == 1 and e.length == 900.0


def test_caso_11b_sin_geometria_segmento_recto():
    G = grafo_sintetico(NODOS, [("A", "B", 0, {"length": 800.0, "travel_time": 50.0})])
    e = mejor_arista(G, "A", "B")
    assert list(e.geometry.coords) == [(-75.67, 4.53), (-75.66, 4.54)]


def test_no_mezcla_atributos():
    # La arista más corta (800 m) NO es la más rápida: no debe mezclarse con la otra.
    e = mejor_arista(grafo_paralelas(), "A", "B")
    assert e.length != 800.0
    assert e.geometry.equals(CURVA) and e.length == 900.0 and e.travel_time == 40.0


def test_sin_arista_lanza_keyerror():
    G = grafo_paralelas()
    with pytest.raises(KeyError, match="B.*A|no hay arista"):
        mejor_arista(G, "B", "A")
