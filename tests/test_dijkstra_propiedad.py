"""Propiedad (caso 13): 200 grafos aleatorios, ambas versiones contra NetworkX."""
import math
import random

import networkx as nx
import pytest

from rutas.r2.adyacencia import construir_adyacencia
from rutas.r2.dijkstra import consultar, dijkstra_cola, dijkstra_lineal
from rutas.r2.ruta import detalle_ruta

SEMILLA = 2026
CANTIDAD = 200


def generar_grafos():
    """200 grafos con ids no consecutivos y desordenados, pesos enteros 0..20,
    algunas aristas paralelas y autolazos."""
    rng = random.Random(SEMILLA)
    grafos = []
    for _ in range(CANTIDAD):
        n = rng.randint(5, 30)
        ids = rng.sample(range(1000, 100000), n)  # distintos, sin orden
        G = nx.MultiDiGraph()
        for id_nodo in ids:  # x, y los pide mejor_arista cuando no hay geometry
            G.add_node(id_nodo, x=-75.0 + id_nodo / 1e6, y=4.5)
        for _ in range(rng.randint(n, 3 * n)):
            u, v = rng.choice(ids), rng.choice(ids)  # u == v da un autolazo
            G.add_edge(u, v, travel_time=rng.randint(0, 20), length=rng.randint(1, 500))
            if rng.random() < 0.2:  # paralela con otro peso
                G.add_edge(u, v, travel_time=rng.randint(0, 20), length=rng.randint(1, 500))
        grafos.append((G, construir_adyacencia(G)))
    return grafos


GRAFOS = generar_grafos()


def test_caso_13_sin_destino():
    for G, red in GRAFOS:
        for id_origen in red.ids:
            origen = red.indice[id_origen]
            dist_l, pred_l, expl_l = dijkstra_lineal(red.adyacencia, origen)
            dist_c, pred_c, expl_c = dijkstra_cola(red.adyacencia, origen)
            assert (dist_l, pred_l, expl_l) == (dist_c, pred_c, expl_c)
            esperado = nx.single_source_dijkstra_path_length(G, id_origen, weight="travel_time")
            for i, id_nodo in enumerate(red.ids):
                if id_nodo in esperado:
                    assert dist_c[i] == esperado[id_nodo]
                else:
                    assert dist_c[i] == math.inf
            assert expl_c == len(esperado)


def test_caso_13_con_destino():
    rng = random.Random(SEMILLA)
    for G, red in GRAFOS:
        for _ in range(10):
            id_origen, id_destino = rng.choice(red.ids), rng.choice(red.ids)
            lineal = consultar(red, id_origen, id_destino, "lineal")
            cola = consultar(red, id_origen, id_destino, "cola_prioridad")
            assert lineal == cola  # mismo tiempo, misma ruta, mismos explorados
            tiempo, ruta, _ = cola
            esperado = nx.single_source_dijkstra_path_length(
                G, id_origen, weight="travel_time").get(id_destino, math.inf)
            assert tiempo == esperado
            if tiempo != math.inf:
                assert ruta[0] == id_origen and ruta[-1] == id_destino
                assert detalle_ruta(G, ruta)[0] == tiempo
            else:
                assert ruta == []
