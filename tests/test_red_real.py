"""Pruebas con la red real descargada (casos 11 real, 14, 15 y componente en radio 2 km).

Necesitan data/processed/ y data/raw/ (se saltan si faltan). Correr con:
    .venv/bin/python -m pytest -m red
"""
import math

import networkx as nx
import numpy as np
import pandas as pd
import pytest
from scipy.spatial import cKDTree

from rutas.config import DATA_PROCESSED, RESULTS_R1, UMBRAL_GZ_BYTES
from rutas.r1.catalogo import cargar_catalogo
from rutas.r1.componente import obtener_componente
from rutas.r1.persistencia import (NOMBRE_GRAFO, cargar_grafo_procesado, cargar_lugares_nodos,
                                   cargar_metadatos, guardar_grafo)
from rutas.r1.ubicacion import ubicar_lugares
from rutas.r1.utm import a_utm

pytestmark = pytest.mark.red


def test_caso_14_velocidades_y_tiempos(grafo_procesado_real):
    """Toda arista tiene velocidad finita > 0 y travel_time = length / (speed_kph / 3.6)."""
    for u, v, key, d in grafo_procesado_real.edges(keys=True, data=True):
        assert math.isfinite(d["speed_kph"]) and d["speed_kph"] > 0, (u, v, key)
        esperado = d["length"] / (d["speed_kph"] / 3.6)
        assert d["travel_time"] == pytest.approx(esperado, abs=1e-6), (u, v, key)


def _primer_tipo(d):
    return d["highway"][0] if isinstance(d["highway"], list) else d["highway"]


def test_ningun_tipo_fuera_de_la_tabla(grafo_procesado_real):
    """En la red real todos los tipos (primer elemento) están en la tabla del grupo."""
    from rutas.r1.pesos import VELOCIDADES
    fuera = {_primer_tipo(d) for _, _, d in grafo_procesado_real.edges(data=True)
             if _primer_tipo(d) not in VELOCIDADES}
    assert fuera == set()


def test_caso_4d_ladder_real_20_kmh(grafo_procesado_real):
    """Toda arista cuyo primer highway es 'ladder' tiene 20 km/h y su tiempo correspondiente."""
    escaleras = [d for _, _, d in grafo_procesado_real.edges(data=True)
                 if _primer_tipo(d) == "ladder"]
    assert escaleras                                   # en la red real hay 4
    for d in escaleras:
        assert d["speed_kph"] == 20
        assert d["travel_time"] == pytest.approx(d["length"] / (20 / 3.6), abs=1e-6)


def test_caso_15_asociacion_contra_ckdtree(grafo_procesado_real):
    """Los 42 lugares quedan en un nodo de la componente; la distancia de la búsqueda lineal
    propia coincide con la de scipy.cKDTree (solo se usa aquí, para verificar)."""
    G = grafo_procesado_real
    lugares = cargar_lugares_nodos(DATA_PROCESSED)
    catalogo = cargar_catalogo()
    assert len(lugares) == 42
    assert list(lugares["id_lugar"]) == list(catalogo["id"])
    assert set(lugares["id_nodo"]) <= set(G.nodes)

    ids = list(G.nodes)
    puntos = np.array([[G.nodes[n]["x_utm"], G.nodes[n]["y_utm"]] for n in ids])
    xs, ys = a_utm(catalogo["longitud"], catalogo["latitud"])
    distancias, _ = cKDTree(puntos).query(np.column_stack([xs, ys]))
    for propia, referencia in zip(lugares["distancia_al_nodo_m"], distancias):
        assert propia == pytest.approx(referencia, abs=1e-6)

    # Y el código actual, vuelto a correr sobre el grafo guardado, reproduce el CSV.
    recalculado = ubicar_lugares(catalogo, G)
    assert list(recalculado["id_nodo"]) == list(lugares["id_nodo"])
    assert recalculado["distancia_al_nodo_m"].tolist() == pytest.approx(
        lugares["distancia_al_nodo_m"].tolist(), abs=1e-6)


def test_componente_radio_2km_igual_a_networkx(red_radio_2km):
    """obtener_componente (OSMnx) da los mismos nodos que la mayor componente de NetworkX."""
    esperada = max(nx.strongly_connected_components(red_radio_2km), key=len)
    obtenida = obtener_componente(red_radio_2km)
    assert set(obtenida.nodes) == set(esperada)
    assert nx.is_strongly_connected(obtenida)


def test_caso_11_guardar_cargar_real(grafo_procesado_real, tmp_path):
    """Guardar y volver a cargar la red real no cambia nada (sin redondeos)."""
    G = grafo_procesado_real
    meta = cargar_metadatos(DATA_PROCESSED)
    umbral = 0 if meta["comprimido"] else UMBRAL_GZ_BYTES
    guardar_grafo(G, tmp_path, umbral_bytes=umbral)
    H = cargar_grafo_procesado(tmp_path)

    assert (H.number_of_nodes(), H.number_of_edges()) == (G.number_of_nodes(), G.number_of_edges())
    suma_g = sum(d["travel_time"] for _, _, d in G.edges(data=True))
    suma_h = sum(d["travel_time"] for _, _, d in H.edges(data=True))
    assert suma_h == pytest.approx(suma_g, abs=1e-6)
    for u, v, key, d in G.edges(keys=True, data=True):
        otro = H[u][v][key]
        assert otro["travel_time"] == pytest.approx(d["travel_time"], abs=1e-9)
        assert otro["length"] == pytest.approx(d["length"], abs=1e-9)

    lugares = cargar_lugares_nodos(DATA_PROCESSED)
    lugares.to_csv(tmp_path / "lugares_nodos.csv", index=False)
    assert ((tmp_path / "lugares_nodos.csv").read_text(encoding="utf-8")
            == (DATA_PROCESSED / "lugares_nodos.csv").read_text(encoding="utf-8"))


def test_metadatos_antes_despues(grafo_procesado_real):
    meta = cargar_metadatos(DATA_PROCESSED)
    assert meta["V_despues"] == grafo_procesado_real.number_of_nodes()
    assert meta["E_despues"] == grafo_procesado_real.number_of_edges()
    assert meta["V_antes"] >= meta["V_despues"] and meta["E_antes"] >= meta["E_despues"]
    existe_plano = (DATA_PROCESSED / NOMBRE_GRAFO).exists()
    existe_gz = (DATA_PROCESSED / (NOMBRE_GRAFO + ".gz")).exists()
    assert existe_plano != existe_gz                       # una sola forma
    assert meta["comprimido"] is existe_gz
    assert meta["archivo_grafo"] == (NOMBRE_GRAFO + ".gz" if existe_gz else NOMBRE_GRAFO)


def test_memoria_real_coincide_con_tamanos(grafo_procesado_real):
    tamanos = pd.read_csv(RESULTS_R1 / "r1_tamanos.csv").set_index("red")
    memoria = pd.read_csv(RESULTS_R1 / "r1_memoria.csv")
    assert len(memoria) == 4
    for _, fila in memoria.iterrows():
        assert fila["V"] == tamanos.loc[fila["red"], "nodos"]
        assert fila["E"] == tamanos.loc[fila["red"], "aristas"]
    meta = cargar_metadatos(DATA_PROCESSED)
    assert tamanos.loc["Red descargada", "nodos"] == meta["V_antes"]
    assert tamanos.loc["Componente fuertemente conexa", "aristas"] == meta["E_despues"]
