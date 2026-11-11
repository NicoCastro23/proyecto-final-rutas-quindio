"""Propiedades del TSP de R4: FB = HK, FB = itertools, voraz >= óptimo y bordes (casos 11 y 12)."""
import itertools
import random

import pytest

from rutas.r4.fuerza_bruta import fuerza_bruta
from rutas.r4.held_karp import held_karp
from rutas.r4.recorrido import costo_recorrido
from rutas.r4.vecino import vecino_mas_cercano

SEMILLA = 2026
INSTANCIAS = 100


def instancias_aleatorias():
    """100 instancias (T, lugares) con k entre 1 y 8, enteros 1..100 asimétricos, s = 0."""
    azar = random.Random(SEMILLA)
    for _ in range(INSTANCIAS):
        k = azar.randint(1, 8)
        n = k + 1
        T = [[0 if i == j else azar.randint(1, 100) for j in range(n)] for i in range(n)]
        lugares = list(range(1, n))
        azar.shuffle(lugares)
        yield T, lugares


def test_caso_11_fb_igual_hk_y_voraz():
    for T, lugares in instancias_aleatorias():
        tiempo_fb, _ = fuerza_bruta(T, 0, lugares)
        tiempo_hk, recorrido = held_karp(T, 0, lugares)
        assert tiempo_hk == pytest.approx(tiempo_fb, abs=1e-6)
        assert recorrido[0] == recorrido[-1] == 0
        assert sorted(recorrido[1:-1]) == sorted(lugares)
        assert costo_recorrido(T, recorrido) == pytest.approx(tiempo_hk, abs=1e-6)
        tiempo_voraz, _ = vecino_mas_cercano(T, 0, lugares)
        assert tiempo_voraz >= tiempo_hk - 1e-9


def test_caso_12_fb_contra_itertools():
    for T, lugares in instancias_aleatorias():
        minimo = min(costo_recorrido(T, [0, *p, 0]) for p in itertools.permutations(lugares))
        assert fuerza_bruta(T, 0, lugares)[0] == pytest.approx(minimo, abs=1e-6)


def test_costo_cero_entre_lugares():
    # Como T03 y T05: dos lugares en el mismo nodo, costo 0 entre ellos en ambos sentidos.
    T = [[0, 7, 7, 20], [7, 0, 0, 9], [7, 0, 0, 11], [20, 9, 11, 0]]
    lugares = [1, 2, 3]
    tiempo_fb, _ = fuerza_bruta(T, 0, lugares)
    tiempo_hk, recorrido = held_karp(T, 0, lugares)
    vecino_mas_cercano(T, 0, lugares)
    assert tiempo_hk == pytest.approx(tiempo_fb, abs=1e-6)
    assert costo_recorrido(T, recorrido) == pytest.approx(tiempo_hk, abs=1e-6)


def test_matriz_simetrica():
    azar = random.Random(SEMILLA)
    n = 7
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            T[i][j] = T[j][i] = azar.randint(1, 100)
    lugares = list(range(1, n))
    tiempo_fb, _ = fuerza_bruta(T, 0, lugares)
    tiempo_hk, recorrido = held_karp(T, 0, lugares)
    assert tiempo_hk == pytest.approx(tiempo_fb, abs=1e-6)
    assert costo_recorrido(T, recorrido[::-1]) == pytest.approx(tiempo_hk, abs=1e-6)
