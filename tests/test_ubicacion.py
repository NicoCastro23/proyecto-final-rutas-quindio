"""Pruebas de rutas/r1/ubicacion.py (casos 7, 8, 9)."""
import numpy as np
import pandas as pd
import pytest

from rutas.r1.ubicacion import nodo_mas_cercano, ubicar_lugares
from tests.conftest import grafo_sintetico


def test_caso_7_vecino_mas_cercano():
    nodos = [(1, 103.0, 104.0), (2, 200.0, 100.0)]
    id_nodo, distancia = nodo_mas_cercano(100.0, 100.0, nodos)
    assert id_nodo == 1
    assert distancia == pytest.approx(5.0)


def test_caso_8_alerta_y_frontera_500(monkeypatch):
    # Se fija la conversión UTM del lugar para que la distancia sea exactamente 600 / 500 m
    # (con pyproj la ida y vuelta añade ruido de 1e-9 m y la frontera sería ambigua).
    monkeypatch.setattr("rutas.r1.ubicacion.a_utm",
                        lambda lons, lats: (np.array([X0]), np.array([Y0])))
    for nodo_x, esperada in ((600.0, True), (500.0, False)):
        G = grafo_con_utm({1: (nodo_x, 0.0)})
        res = ubicar_lugares(catalogo_en_utm([("L1", 0.0, 0.0)]), G)
        assert res.loc[0, "distancia_al_nodo_m"] == pytest.approx(nodo_x)
        assert bool(res.loc[0, "alerta_500m"]) is esperada


def test_caso_9_empate_menor_id():
    nodos = [(7, 10.0, 0.0), (3, -10.0, 0.0)]
    assert nodo_mas_cercano(0.0, 0.0, nodos)[0] == 3
    assert nodo_mas_cercano(0.0, 0.0, nodos[::-1])[0] == 3


def test_lugar_sobre_nodo_distancia_cero():
    assert nodo_mas_cercano(5.0, 7.0, [(9, 5.0, 7.0), (4, 50.0, 70.0)]) == (9, 0.0)


def test_ubicar_lugares_columnas_y_orden():
    G = grafo_con_utm({1: (0.0, 0.0), 2: (1000.0, 0.0)})
    cat = catalogo_en_utm([("L2", 990.0, 0.0), ("L1", 3.0, 4.0), ("L3", 0.0, 800.0)])
    res = ubicar_lugares(cat, G)
    assert list(res.columns) == ["id_lugar", "id_nodo", "distancia_al_nodo_m", "alerta_500m"]
    assert list(res["id_lugar"]) == ["L2", "L1", "L3"]  # mismo orden del catálogo
    assert list(res["id_nodo"]) == [2, 1, 1]
    assert res["distancia_al_nodo_m"].tolist() == pytest.approx([10.0, 5.0, 800.0])
    assert list(res["alerta_500m"]) == [False, False, True]  # el alertado se conserva (3 filas)


# --- ayudas: coordenadas relativas a un origen UTM fijo dentro del Quindío ---
X0, Y0 = 425_000.0, 500_000.0


def grafo_con_utm(nodos_utm):
    """Grafo sintético cuyos nodos ya traen x_utm, y_utm (relativos al origen)."""
    G = grafo_sintetico({n: (-75.6, 4.5) for n in nodos_utm}, [])
    for n, (x, y) in nodos_utm.items():
        G.nodes[n]["x_utm"], G.nodes[n]["y_utm"] = X0 + x, Y0 + y
    return G


def catalogo_en_utm(lugares):
    """Catálogo mínimo (id, latitud, longitud) con lugares relativos al mismo origen."""
    from rutas.r1.utm import a_latlon
    lons, lats = a_latlon([X0 + x for _, x, _ in lugares], [Y0 + y for _, _, y in lugares])
    return pd.DataFrame({"id": [i for i, _, _ in lugares], "latitud": lats, "longitud": lons})
