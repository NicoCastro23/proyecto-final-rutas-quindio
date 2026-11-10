"""Pruebas de detalle_ruta (R2, caso 12 y bordes de ruta)."""
import pytest

from rutas.r2.adyacencia import construir_adyacencia
from rutas.r2.dijkstra import consultar
from rutas.r2.ruta import detalle_ruta
from tests.conftest import grafo_sintetico

NODOS = {1: (-75.6, 4.5), 2: (-75.5, 4.5), 3: (-75.4, 4.5), 4: (-75.3, 4.5), 5: (-75.2, 4.5)}


def arista(u, v, tiempo, largo):
    return (u, v, {"travel_time": tiempo, "length": largo})


def test_caso_12_detalle_usa_mejor_arista():
    # Dos paralelas A->B: 50 s / 800 m y 40 s / 900 m; la mejor es la de 40 s
    G = grafo_sintetico(NODOS, [arista(1, 2, 50, 800), arista(1, 2, 40, 900)])
    red = construir_adyacencia(G)
    tiempo, ruta, _ = consultar(red, 1, 2, "cola_prioridad")
    assert tiempo == 40 and ruta == [1, 2]
    assert detalle_ruta(G, ruta) == (40, 900)


def test_ruta_g1():
    # G1 (A=1..E=5); ruta del caso 3: A, C, B, D, E con tiempo 1 + 2 + 1 + 3 = 7
    G = grafo_sintetico(NODOS, [
        arista(1, 2, 4, 400), arista(1, 3, 1, 100), arista(3, 2, 2, 250),
        arista(2, 4, 1, 120), arista(3, 4, 5, 500), arista(4, 5, 3, 330)])
    tiempo, ruta, _ = consultar(construir_adyacencia(G), 1, 5)
    assert ruta == [1, 3, 2, 4, 5]
    assert detalle_ruta(G, ruta) == (7, 100 + 250 + 120 + 330)


def test_ruta_de_un_nodo():
    G = grafo_sintetico(NODOS, [arista(1, 2, 40, 900)])
    assert detalle_ruta(G, [1]) == (0, 0)


def test_ruta_vacia_error():
    G = grafo_sintetico(NODOS, [arista(1, 2, 40, 900)])
    with pytest.raises(ValueError):
        detalle_ruta(G, [])
