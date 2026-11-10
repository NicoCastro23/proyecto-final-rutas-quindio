"""Pruebas de las dos versiones de Dijkstra con los casos resueltos a mano (R2, casos 1 a 12)."""
import copy
import math

import pytest

from rutas.r2.dijkstra import VERSIONES, consultar, dijkstra_cola, dijkstra_lineal, reconstruir_ruta
from tests.conftest import red_desde_aristas

INF = math.inf
VERSION = pytest.mark.parametrize("version", ["lineal", "cola_prioridad"])

# G1 de la spec: A=1, B=2, C=3, D=4, E=5, F=6 (F aislado)
ARISTAS_G1 = [(1, 2, 4), (1, 3, 1), (3, 2, 2), (2, 4, 1), (3, 4, 5), (4, 5, 3)]


def g1(extra=()):
    return red_desde_aristas(ARISTAS_G1 + list(extra), nodos=[6])


@VERSION
def test_caso_1_a_b(version):
    assert consultar(g1(), 1, 2, version) == (3, [1, 3, 2], 3)


@VERSION
def test_caso_2_a_d_entrada_obsoleta(version):
    assert consultar(g1(), 1, 4, version) == (4, [1, 3, 2, 4], 4)


@VERSION
def test_caso_3_a_e(version):
    assert consultar(g1(), 1, 5, version) == (7, [1, 3, 2, 4, 5], 5)


@VERSION
def test_caso_4_origen_igual_destino(version):
    assert consultar(g1(), 1, 1, version) == (0, [1], 1)


@VERSION
def test_caso_5_a_f_inalcanzable(version):
    assert consultar(g1(), 1, 6, version) == (INF, [], 5)


@VERSION
def test_caso_6_e_a_inalcanzable(version):
    assert consultar(g1(), 5, 1, version) == (INF, [], 1)


@VERSION
def test_caso_8_peso_cero(version):
    # B->E de 0 s: A->E = 3 por A, C, B, E
    assert consultar(g1([(2, 5, 0)]), 1, 5, version)[:2] == (3, [1, 3, 2, 5])


@VERSION
def test_caso_11_desempate_por_id(version):
    red = red_desde_aristas([(1, 2, 1), (1, 3, 1), (2, 4, 1), (3, 4, 1)])
    assert consultar(red, 1, 4, version) == (2, [1, 2, 4], 4)


@VERSION
def test_caso_12_paralelas_y_autolazo(version):
    red = red_desde_aristas([(1, 2, 50), (1, 2, 40), (1, 1, 5), (2, 1, 10)])
    assert consultar(red, 1, 2, version)[:2] == (40, [1, 2])


@VERSION
def test_caso_7_sin_destino(version):
    red = g1()
    esperado = {1: [0, 3, 1, 4, 7], 2: [INF, 0, INF, 1, 4], 3: [INF, 2, 0, 3, 6],
                4: [INF, INF, INF, 0, 3], 5: [INF, INF, INF, INF, 0]}
    for origen, fila in esperado.items():
        dist, _, _ = VERSIONES[version](red.adyacencia, red.indice[origen])
        assert [dist[red.indice[x]] for x in range(1, 6)] == fila


@VERSION
def test_sin_destino_listas_tamano_V(version):
    red = g1()
    funcion = VERSIONES[version]
    dist, pred, _ = funcion(red.adyacencia, red.indice[1])
    assert len(dist) == len(pred) == 6
    assert pred[red.indice[1]] is None
    assert pred[red.indice[6]] is None and dist[red.indice[6]] == INF
    # con destino la ruta es de índices (A -> C -> B)
    assert funcion(red.adyacencia, 0, 1) == (3, [0, 2, 1], 3)


@VERSION
def test_no_modifica_adyacencia(version):
    red = g1()
    antes = copy.deepcopy(red.adyacencia)
    VERSIONES[version](red.adyacencia, 0)
    VERSIONES[version](red.adyacencia, 0, 4)
    assert red.adyacencia == antes


def test_reconstruir_ruta():
    pred = [None, 0, 1, None]
    assert reconstruir_ruta(pred, 0, 2) == [0, 1, 2]
    assert reconstruir_ruta(pred, 0, 0) == [0]
    assert reconstruir_ruta(pred, 0, 3) == []


def test_consultar_traduce_ids():
    red = red_desde_aristas([(30, 10, 1), (10, 20, 2)])
    for version in ("lineal", "cola_prioridad"):
        assert consultar(red, 30, 20, version) == (3, [30, 10, 20], 3)


def test_consultar_id_inexistente_keyerror():
    red = g1()
    with pytest.raises(KeyError, match="99"):
        consultar(red, 99, 1)
    with pytest.raises(KeyError, match="77"):
        consultar(red, 1, 77)


def test_consultar_version_desconocida():
    with pytest.raises(ValueError):
        consultar(g1(), 1, 2, "bellman")


def test_caso_10_versiones_coinciden():
    # Casos 1 a 8 y 11: con y sin destino, mismas salidas completas (incluidas dist y pred)
    redes = [g1(), g1([(2, 5, 0)]),
             red_desde_aristas([(1, 2, 1), (1, 3, 1), (2, 4, 1), (3, 4, 1)])]
    for red in redes:
        V = len(red.ids)
        for origen in range(V):
            assert dijkstra_lineal(red.adyacencia, origen) == dijkstra_cola(red.adyacencia, origen)
            for destino in range(V):
                assert (dijkstra_lineal(red.adyacencia, origen, destino)
                        == dijkstra_cola(red.adyacencia, origen, destino))
