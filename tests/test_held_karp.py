"""Held-Karp: tabla (caso 3), contador (caso 15) y lecturas reales de T."""
import inspect
import math
import random

import pytest

from rutas.r4.held_karp import held_karp, tabla_held_karp
from tests.test_tsp_clase import T_CLASE

# Caso 3 de la spec: {(máscara, lugar): (costo, padre)}. El lugar L cae en el índice local L - 1.
CELDAS_CASO_3 = {
    (0b001, 1): (10, None), (0b010, 2): (15, None), (0b100, 3): (20, None),
    (0b011, 1): (28, 2), (0b011, 2): (19, 1),
    (0b101, 1): (28, 3), (0b101, 3): (20, 1),
    (0b110, 2): (29, 3), (0b110, 3): (27, 2),
    (0b111, 1): (35, 3), (0b111, 2): (29, 3), (0b111, 3): (31, 2),
}


def test_caso_3_tabla():
    costo, padre = tabla_held_karp(T_CLASE, 0, [1, 2, 3])
    for (mascara, lugar), (c, p) in CELDAS_CASO_3.items():
        assert costo[mascara][lugar - 1] == c, (bin(mascara), lugar)
        esperado = None if p is None else p - 1
        assert padre[mascara][lugar - 1] == esperado, (bin(mascara), lugar)
    assert costo[0b001][0] == 10 and padre[0b001][0] is None
    assert costo[0b011][0] == 28 and padre[0b011][0] == 1
    assert costo[0b111][1] == 29 and padre[0b111][1] == 2


def test_tabla_celdas_no_usadas():
    costo, padre = tabla_held_karp(T_CLASE, 0, [1, 2, 3])
    assert len(costo) == 8 and all(len(fila) == 3 for fila in costo)
    assert len(padre) == 8 and all(len(fila) == 3 for fila in padre)
    usadas = {(m, l - 1) for (m, l) in CELDAS_CASO_3}
    for mascara in range(8):
        for j in range(3):
            if (mascara, j) not in usadas:
                assert costo[mascara][j] == math.inf, (mascara, j)
                assert padre[mascara][j] is None, (mascara, j)


def test_tabla_lugares_desordenados():
    assert tabla_held_karp(T_CLASE, 0, [3, 1, 2]) == tabla_held_karp(T_CLASE, 0, [1, 2, 3])


def matriz_aleatoria(k, semilla=2026):
    """Matriz (k + 1) x (k + 1) asimétrica de enteros 1..100 (la partida es el índice 0)."""
    azar = random.Random(semilla)
    n = k + 1
    return [[0 if i == j else azar.randint(1, 100) for j in range(n)] for i in range(n)]


@pytest.mark.parametrize("k, esperado", [(3, 18), (5, 170), (8, 3600),
                                         (10, 23060), (12, 135192)])
def test_caso_15_contador(k, esperado):
    c = [0]
    held_karp(matriz_aleatoria(k), 0, list(range(1, k + 1)), contador=c)
    assert c[0] == esperado


class FilaContada(list):
    """Fila de T que cuenta cada lectura T[i][j] en un contador compartido."""

    def __init__(self, fila, lecturas):
        super().__init__(fila)
        self.lecturas = lecturas

    def __getitem__(self, indice):
        self.lecturas[0] += 1
        return super().__getitem__(indice)


@pytest.mark.parametrize("k", [3, 5, 8])
def test_contador_igual_a_lecturas_de_T(k):
    lecturas = [0]
    T = [FilaContada(fila, lecturas) for fila in matriz_aleatoria(k)]
    c = [0]
    held_karp(T, 0, list(range(1, k + 1)), contador=c)
    assert lecturas[0] == c[0]


def test_sin_contador_por_defecto():
    assert inspect.signature(held_karp).parameters["contador"].default is None
    assert held_karp(T_CLASE, 0, [1, 2, 3]) == (35, [0, 1, 3, 2, 0])
