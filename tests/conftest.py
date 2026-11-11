"""Fixtures y helpers compartidos por las pruebas (R1, R2 y R3)."""
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


def cargar_casos_r3():
    """Casos de la envolvente (tests/datos/red_clase.json): (nodos {id: (x, y)} como int, sección R3)."""
    datos = json.loads((RAIZ / "tests" / "datos" / "red_clase.json").read_text(encoding="utf-8"))
    nodos = {int(i): (int(n["x"]), int(n["y"])) for i, n in datos["red"]["nodos"].items()}
    return nodos, datos["R3"]


def comprobar_envolvente(vertices, puntos):
    """Invariantes geométricos de una envolvente (caso 13), sin usar SciPy. Lanza AssertionError."""
    from rutas.r3.envolvente import cruz
    puntos = set(puntos)
    h = len(vertices)
    assert len(set(vertices)) == h, "vértices repetidos"
    assert set(vertices) <= puntos, "hay vértices que no son puntos de la entrada"
    if h:
        assert vertices[0] == min(vertices, key=lambda p: (p[1], p[0])), "no empieza por el menor (y, x)"
    if h >= 3:
        for i in range(h):
            # Tres vértices seguidos giran siempre a la izquierda: antihorario y sin alineados
            assert cruz(vertices[i], vertices[(i + 1) % h], vertices[(i + 2) % h]) > 0, "no es convexo estricto"
        if set(vertices) != puntos:       # si todos son vértices no hay nada que comprobar (y sería O(n*h))
            for i in range(h):
                lado = (vertices[i], vertices[(i + 1) % h])
                assert all(cruz(*lado, p) >= 0 for p in puntos), "hay un punto fuera del polígono"
    if h == 2:
        a, b = vertices
        assert all(cruz(a, b, p) == 0 for p in puntos), "con 2 vértices todos deben estar alineados"
        assert all(a <= p <= b for p in puntos), "los puntos deben estar entre los dos extremos"


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
