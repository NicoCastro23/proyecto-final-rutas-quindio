"""Propiedades de QuickHull: conjuntos aleatorios contra SciPy y casos donde todos son vértices."""
import math
import random

import pytest

from rutas.r3.envolvente import envolvente, normalizar
from rutas.r3.puntos import puntos_cuadrado, redondear
from rutas.r3.referencia import vertices_scipy
from tests.conftest import comprobar_envolvente


def test_caso_11_aleatorios_vs_scipy():
    azar = random.Random(2026)
    comparados = 0
    for _ in range(100):
        # Tamaños y rangos variados (n entre 3 y 200): con pocos puntos en una cuadrícula chica abundan
        # los alineados sobre los lados y los repetidos (no se pasa por preparar_puntos)
        n = azar.randint(3, azar.choice((8, 30, 200)))
        rango = azar.choice((2, 5, 10))
        puntos = [(azar.randint(-rango, rango), azar.randint(-rango, rango)) for _ in range(n)]
        propia = envolvente(puntos)
        comprobar_envolvente(propia, puntos)
        if len(propia) < 3:                  # degenerado: SciPy lanza QhullError, solo valen los invariantes
            continue
        referencia = vertices_scipy(puntos)
        assert set(propia) == set(referencia)
        assert normalizar(propia) == referencia
        comparados += 1
    assert comparados >= 90


@pytest.mark.parametrize("n", [1_000, 10_000, 50_000])
def test_caso_12_cuadrados(n):
    puntos = puntos_cuadrado(n)
    propia = envolvente(puntos)
    assert set(propia) == set(vertices_scipy(puntos))
    assert normalizar(propia) == vertices_scipy(puntos)
    comprobar_envolvente(propia, puntos)
    esperado = (8 / 3) * math.log(len(puntos))          # Rényi y Sulanke: vértices esperados
    assert 0.5 * esperado <= len(propia) <= 2 * esperado


def test_caso_15_circulo():
    # 2 000 puntos sobre una circunferencia de radio 10^6: todos son vértices
    n = 2_000
    puntos = [(redondear(10**6 * math.cos(2 * math.pi * k / n)),
               redondear(10**6 * math.sin(2 * math.pi * k / n))) for k in range(n)]
    assert len(set(puntos)) == n
    propia = envolvente(puntos)
    assert len(propia) == n
    assert normalizar(propia) == vertices_scipy(puntos)
    comprobar_envolvente(propia, puntos)


def test_caso_16_parabola():
    # (k, k^2) es convexa de forma estricta (verificado con enteros por comprobar_envolvente)
    puntos = [(k, k * k) for k in range(5_000)]
    propia = envolvente(puntos)
    assert len(propia) == 5_000 and propia[0] == (0, 0)
    comprobar_envolvente(propia, puntos)
