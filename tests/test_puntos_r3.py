"""Pruebas de rutas/r3/puntos.py: redondeo, repetidos y cuadrado aleatorio."""
import numpy as np
import pytest

from rutas.r3.puntos import LADO, SEMILLA, preparar_puntos, puntos_cuadrado, redondear


def test_caso_9_redondeo():
    assert redondear(2.5) == 3
    assert redondear(-0.5) == 0            # empates .5 hacia +infinito
    assert redondear(2.4999) == 2
    assert redondear(-2.5) == -2
    assert type(redondear(2.5)) is int
    assert type(redondear(np.float64(2.5))) is int and redondear(np.float64(2.5)) == 3


def test_preparar_quita_repetidos():
    # (0, 0) repetido y (0.4, 0.4) que tras redondear coincide con (0, 0)
    puntos = preparar_puntos([0, 0, 1, 0, 0.4], [0, 0, 0, 1, 0.4])
    assert puntos == [(0, 0), (0, 1), (1, 0)]
    assert all(type(x) is int and type(y) is int for x, y in puntos)


def test_preparar_ordena():
    puntos = preparar_puntos([3, 1, 2, 1, 3], [1, 5, 2, 4, 1])
    assert puntos == sorted(set(puntos)) and len(puntos) == 4


def test_preparar_largos_distintos():
    with pytest.raises(ValueError):
        preparar_puntos([1, 2, 3], [1, 2])


def test_puntos_cuadrado_semilla():
    assert SEMILLA == 2026 and LADO == 10**6
    puntos = puntos_cuadrado(1000)
    assert puntos == puntos_cuadrado(1000)
    assert puntos != puntos_cuadrado(1000, semilla=7)
    assert 990 < len(puntos) <= 1000
    assert all(0 <= x < LADO and 0 <= y < LADO for x, y in puntos)
    assert puntos == sorted(set(puntos))
