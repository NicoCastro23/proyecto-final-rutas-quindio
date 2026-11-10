"""Fixtures y helpers compartidos por las pruebas (R1 y R2)."""
import json

import networkx as nx
import pytest

from rutas.config import DATA_PROCESSED, DATA_RAW, RAIZ
from rutas.r2.adyacencia import construir_adyacencia


def grafo_sintetico(nodos, aristas):
    """Construye un MultiDiGraph pequeño con el formato que deja OSMnx.

    nodos:   dict {id: (lon, lat)}
    aristas: lista de tuplas (u, v, atributos) o (u, v, key, atributos)
    Se pone crs y x, y en cada nodo porque ox.add_edge_speeds llama a graph_to_gdfs.
    """
    G = nx.MultiDiGraph()
    G.graph["crs"] = "epsg:4326"
    for id_nodo, (lon, lat) in nodos.items():
        G.add_node(id_nodo, x=lon, y=lat)
    for arista in aristas:
        if len(arista) == 3:
            u, v, atributos = arista
            G.add_edge(u, v, **atributos)
        else:
            u, v, key, atributos = arista
            G.add_edge(u, v, key=key, **atributos)
    return G


def red_desde_aristas(aristas, nodos=None):
    """Red indexada de R2 desde tuplas (u, v, travel_time) con ids enteros pequeños.

    nodos: ids extra sin aristas (p. ej. un nodo aislado). Pasa por construir_adyacencia,
    igual que la red real (aristas paralelas y autolazos incluidos).
    """
    G = nx.MultiDiGraph()
    G.add_nodes_from(nodos or [])
    for u, v, tiempo in aristas:
        G.add_edge(u, v, travel_time=tiempo)
    return construir_adyacencia(G)


def cargar_red_clase():
    """Red de la clase de Dijkstra (tests/datos/red_clase.json) restringida a la componente 1-7.

    Pesos en minutos, con la arista paralela 2->3 incluida. Devuelve (red, seccion R2 del JSON).
    """
    datos = json.loads((RAIZ / "tests" / "datos" / "red_clase.json").read_text(encoding="utf-8"))
    aristas = [(a["u"], a["v"], float(a["min"])) for a in datos["red"]["aristas"]
               if a["u"] <= 7 and a["v"] <= 7]
    return red_desde_aristas(aristas), datos["R2"]


def _ruta_grafo_procesado():
    for nombre in ("grafo_componente.graphml", "grafo_componente.graphml.gz"):
        if (DATA_PROCESSED / nombre).exists():
            return DATA_PROCESSED / nombre
    return None


@pytest.fixture
def grafo_procesado_real():
    """Grafo procesado real (.graphml o .graphml.gz); se salta si no existe."""
    if _ruta_grafo_procesado() is None:
        pytest.skip("falta data/processed/grafo_componente.graphml[.gz]")
    from rutas.r1.persistencia import cargar_grafo_procesado
    return cargar_grafo_procesado(DATA_PROCESSED)


@pytest.fixture
def red_radio_2km():
    """Red cruda de radio 2 km; se salta si no se ha descargado."""
    ruta = DATA_RAW / "radio_2km.graphml"
    if not ruta.exists():
        pytest.skip("falta data/raw/radio_2km.graphml")
    import osmnx as ox
    return ox.load_graphml(ruta)
